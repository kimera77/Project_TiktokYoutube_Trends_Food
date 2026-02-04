"""
Lógica de predicción usando modelos XGBoost y LightGBM entrenados
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class VideoPredictor:
    """
    Clase para cargar modelos y realizar predicciones de engagement
    """
    
    def __init__(self, models_path="../03_Modelo_XGBoost_LightGBM"):
        """
        Inicializa el predictor cargando los modelos y escaladores
        
        Args:
            models_path (str): Ruta a la carpeta con los modelos entrenados
        """
        self.models_path = Path(models_path)
        self.load_models()
    
    def load_models(self):
        """
        Carga todos los modelos, escaladores y encoders necesarios
        """
        try:
            # Cargar modelos
            self.xgb_model = joblib.load(self.models_path / 'xgboost_engagement_regressor.pkl')
            self.lgb_model = joblib.load(self.models_path / 'lightgbm_engagement_classifier.pkl')
            
            # Cargar escaladores y encoders
            self.scaler = joblib.load(self.models_path / 'scaler_xgb.pkl')
            
            # Intentar cargar label encoder (puede tener nombre diferente)
            try:
                self.label_encoder = joblib.load(self.models_path / 'label_encoder_category.pkl')
            except:
                # Si no existe, crear uno por defecto
                from sklearn.preprocessing import LabelEncoder
                self.label_encoder = LabelEncoder()
                self.label_encoder.classes_ = np.array(['Bajo', 'Medio', 'Alto', 'Viral'])
            
            # Obtener nombres de características del modelo
            if hasattr(self.xgb_model, 'get_booster'):
                self.feature_names = self.xgb_model.get_booster().feature_names
            else:
                self.feature_names = None
            
            print("✅ Modelos cargados exitosamente")
            
        except Exception as e:
            print(f"❌ Error al cargar modelos: {e}")
            raise
    
    def prepare_features(self, features_dict):
        """
        Prepara las características en el formato correcto para los modelos
        
        Args:
            features_dict (dict): Diccionario con todas las características
            
        Returns:
            np.array: Array con características preparadas
        """
        # Obtener los nombres de features del scaler
        expected_features = list(self.scaler.feature_names_in_)
        
        # Crear diccionario solo con las features esperadas (excluir 'title')
        filtered_features = {k: v for k, v in features_dict.items() if k in expected_features}
        
        # Crear DataFrame con las features en el orden exacto del scaler
        df = pd.DataFrame([filtered_features])
        
        # Asegurar que todas las columnas estén presentes en el orden correcto
        for col in expected_features:
            if col not in df.columns:
                df[col] = 0
        
        # Reordenar columnas según el orden del scaler
        df = df[expected_features]
        
        # Escalar las características
        features_scaled = self.scaler.transform(df)
        
        return features_scaled
    
    def predict_engagement_rate(self, features_dict):
        """
        Predice la tasa de engagement usando XGBoost
        
        Args:
            features_dict (dict): Diccionario con todas las características
            
        Returns:
            float: Tasa de engagement predicha (%)
        """
        features = self.prepare_features(features_dict)
        engagement_rate = self.xgb_model.predict(features)[0]
        
        # Asegurar que esté en rango razonable
        engagement_rate = max(0, min(100, engagement_rate))
        
        return engagement_rate
    
    def predict_engagement_category(self, features_dict):
        """
        Predice la categoría de engagement usando LightGBM
        
        Args:
            features_dict (dict): Diccionario con todas las características
            
        Returns:
            tuple: (categoría, probabilidades)
        """
        features = self.prepare_features(features_dict)
        
        # Predicción de categoría
        category_encoded = self.lgb_model.predict(features)[0]
        category = self.label_encoder.inverse_transform([category_encoded])[0]
        
        # Probabilidades por clase
        probabilities = self.lgb_model.predict_proba(features)[0]
        prob_dict = {
            self.label_encoder.inverse_transform([i])[0]: prob 
            for i, prob in enumerate(probabilities)
        }
        
        return category, prob_dict
    
    def predict_full(self, features_dict):
        """
        Realiza predicción completa: engagement rate y categoría
        
        Args:
            features_dict (dict): Diccionario con todas las características
            
        Returns:
            dict: Diccionario con todas las predicciones
        """
        # Predicción de engagement rate
        engagement_rate = self.predict_engagement_rate(features_dict)
        
        # Predicción de categoría
        category, probabilities = self.predict_engagement_category(features_dict)
        
        # Determinar confianza de la predicción
        max_prob = max(probabilities.values())
        confidence = "Alta" if max_prob > 0.6 else "Media" if max_prob > 0.4 else "Baja"
        
        return {
            'engagement_rate': engagement_rate,
            'category': category,
            'category_probabilities': probabilities,
            'confidence': confidence,
            'max_probability': max_prob
        }
    
    def get_feature_importance(self, top_n=10):
        """
        Obtiene la importancia de características del modelo XGBoost
        
        Args:
            top_n (int): Número de características más importantes a retornar
            
        Returns:
            pd.DataFrame: DataFrame con características e importancias
        """
        importances = self.xgb_model.feature_importances_
        
        # Obtener nombres de features del scaler (fuente confiable)
        feature_names = list(self.scaler.feature_names_in_)
        
        # Verificar que coincidan las dimensiones
        if len(feature_names) != len(importances):
            raise ValueError(f"Mismatch: {len(feature_names)} nombres vs {len(importances)} importancias")
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False).head(top_n)
        
        return importance_df
