"""
Página de Dashboard - Visualizaciones del modelo
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from pathlib import Path
import sys

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from predictor import VideoPredictor

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard del Modelo")
st.markdown("### Visualiza el rendimiento y características de los modelos de Machine Learning")

# Inicializar predictor
@st.cache_resource
def load_predictor():
    return VideoPredictor(models_path="../03_Modelo_XGBoost_LightGBM")

try:
    predictor = load_predictor()
    
    # Cargar métricas guardadas
    metrics_xgb_path = Path("../03_Modelo_XGBoost_LightGBM/xgb_metrics.json")
    metrics_lgb_path = Path("../03_Modelo_XGBoost_LightGBM/lgb_metrics.json")
    
    if metrics_xgb_path.exists():
        with open(metrics_xgb_path, 'r') as f:
            metrics_xgb = json.load(f)
    else:
        metrics_xgb = None
    
    if metrics_lgb_path.exists():
        with open(metrics_lgb_path, 'r') as f:
            metrics_lgb = json.load(f)
    else:
        metrics_lgb = None
    
    # Tabs para organizar contenido
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Métricas del Modelo",
        "🎯 Importancia de Características",
        "🔍 Análisis SHAP",
        "📊 Matriz de Confusión"
    ])
    
    # ===== TAB 1: Métricas del Modelo =====
    with tab1:
        st.markdown("### 📈 Rendimiento de los Modelos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔵 XGBoost Regressor (Engagement Rate)")
            
            if metrics_xgb:
                # Mostrar métricas clave
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    r2 = metrics_xgb.get('test_r2', 0)
                    st.metric("R² Score", f"{r2:.4f}", 
                             delta="Mejor" if r2 > 0.05 else "Mejorable",
                             delta_color="normal")
                
                with metric_col2:
                    mae = metrics_xgb.get('test_mae', 0)
                    st.metric("MAE", f"{mae:.4f}%", 
                             help="Error Absoluto Medio")
                
                with metric_col3:
                    rmse = metrics_xgb.get('test_rmse', 0)
                    st.metric("RMSE", f"{rmse:.4f}%", 
                             help="Raíz del Error Cuadrático Medio")
                
                # Gráfico de comparación Train vs Test
                fig_xgb = go.Figure()
                
                metrics_names = ['R²', 'MAE', 'RMSE']
                train_values = [
                    metrics_xgb.get('train_r2', 0),
                    metrics_xgb.get('train_mae', 0) / 10,  # Escalar para visualización
                    metrics_xgb.get('train_rmse', 0) / 10
                ]
                test_values = [
                    metrics_xgb.get('test_r2', 0),
                    metrics_xgb.get('test_mae', 0) / 10,
                    metrics_xgb.get('test_rmse', 0) / 10
                ]
                
                fig_xgb.add_trace(go.Bar(
                    name='Train',
                    x=metrics_names,
                    y=train_values,
                    marker_color='lightblue'
                ))
                
                fig_xgb.add_trace(go.Bar(
                    name='Test',
                    x=metrics_names,
                    y=test_values,
                    marker_color='darkblue'
                ))
                
                fig_xgb.update_layout(
                    title="Comparación Train vs Test (XGBoost)",
                    barmode='group',
                    yaxis_title="Valor de Métrica",
                    height=400
                )
                
                st.plotly_chart(fig_xgb, use_container_width=True)
                
            else:
                st.warning("Métricas de XGBoost no disponibles")
        
        with col2:
            st.markdown("#### 🟢 LightGBM Classifier (Categoría)")
            
            if metrics_lgb:
                # Mostrar métricas clave
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    acc = metrics_lgb.get('test_accuracy', 0)
                    st.metric("Accuracy", f"{acc*100:.2f}%", 
                             delta="Bueno" if acc > 0.5 else "Mejorable",
                             delta_color="normal")
                
                with metric_col2:
                    prec = metrics_lgb.get('test_precision_macro', 0)
                    st.metric("Precision", f"{prec*100:.2f}%", 
                             help="Precisión Macro")
                
                with metric_col3:
                    rec = metrics_lgb.get('test_recall_macro', 0)
                    st.metric("Recall", f"{rec*100:.2f}%", 
                             help="Recall Macro")
                
                # Gráfico de comparación Train vs Test
                fig_lgb = go.Figure()
                
                metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
                train_values = [
                    metrics_lgb.get('train_accuracy', 0),
                    metrics_lgb.get('train_precision_macro', 0),
                    metrics_lgb.get('train_recall_macro', 0),
                    metrics_lgb.get('train_f1_macro', 0)
                ]
                test_values = [
                    metrics_lgb.get('test_accuracy', 0),
                    metrics_lgb.get('test_precision_macro', 0),
                    metrics_lgb.get('test_recall_macro', 0),
                    metrics_lgb.get('test_f1_macro', 0)
                ]
                
                fig_lgb.add_trace(go.Bar(
                    name='Train',
                    x=metrics_names,
                    y=train_values,
                    marker_color='lightgreen'
                ))
                
                fig_lgb.add_trace(go.Bar(
                    name='Test',
                    x=metrics_names,
                    y=test_values,
                    marker_color='darkgreen'
                ))
                
                fig_lgb.update_layout(
                    title="Comparación Train vs Test (LightGBM)",
                    barmode='group',
                    yaxis_title="Score",
                    height=400
                )
                
                st.plotly_chart(fig_lgb, use_container_width=True)
                
            else:
                st.warning("Métricas de LightGBM no disponibles")
        
        # Información adicional
        st.markdown("---")
        st.markdown("""
        #### 📝 Interpretación de Métricas
        
        - **R² Score**: Mide qué tan bien el modelo explica la variabilidad del engagement. 
          Valor de 0.07 indica que el engagement es difícil de predecir solo con metadatos.
        - **MAE/RMSE**: Error promedio en puntos de engagement rate. Menor es mejor.
        - **Accuracy**: Porcentaje de clasificaciones correctas (Bajo/Medio/Alto/Viral).
        - **Precision/Recall**: Balance entre predicciones correctas y cobertura de casos reales.
        """)
    
    # ===== TAB 2: Importancia de Características =====
    with tab2:
        st.markdown("### 🎯 Características Más Importantes")
        st.markdown("Las características que más influyen en la predicción del engagement:")
        
        # Obtener importancias
        importance_df = predictor.get_feature_importance(top_n=15)
        
        # Gráfico de barras horizontal
        fig_importance = px.bar(
            importance_df.sort_values('importance'),
            x='importance',
            y='feature',
            orientation='h',
            title="Top 15 Características Más Importantes (XGBoost)",
            labels={'importance': 'Importancia', 'feature': 'Característica'},
            color='importance',
            color_continuous_scale='Viridis'
        )
        
        fig_importance.update_layout(
            height=600,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_importance, use_container_width=True)
        
        # Tabla con detalles
        st.markdown("#### 📋 Tabla de Importancias")
        st.dataframe(
            importance_df.style.background_gradient(cmap='YlOrRd', subset=['importance']),
            use_container_width=True
        )
        
        st.info("""
        💡 **Interpretación**: 
        - `log_subscribers`: El tamaño del canal es el factor más importante
        - `duration` y `log_duration`: La duración del video tiene gran impacto
        - `sentiment_compound`: El sentimiento del título afecta el engagement
        - Características temporales y del título también influyen significativamente
        """)
    
    # ===== TAB 3: Análisis SHAP =====
    with tab3:
        st.markdown("### 🔍 Análisis SHAP (SHapley Additive exPlanations)")
        st.markdown("Explica cómo cada característica contribuye a la predicción:")
        
        # Cargar imágenes SHAP si existen
        shap_summary_path = Path("../03_Modelo_XGBoost_LightGBM/shap_summary.png")
        shap_bar_path = Path("../03_Modelo_XGBoost_LightGBM/shap_importance.png")
        
        if shap_summary_path.exists() and shap_bar_path.exists():
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### SHAP Summary Plot")
                st.image(str(shap_summary_path), 
                        caption="Distribución de valores SHAP por característica",
                        use_container_width=True)
            
            with col2:
                st.markdown("#### SHAP Feature Importance")
                st.image(str(shap_bar_path), 
                        caption="Importancia promedio absoluta de características",
                        use_container_width=True)
            
            st.markdown("""
            #### 📊 Cómo Leer los Gráficos SHAP
            
            - **Eje X**: Impacto en la predicción (positivo = aumenta engagement, negativo = disminuye)
            - **Color**: Valor de la característica (rojo = alto, azul = bajo)
            - **Posición vertical**: Características ordenadas por importancia
            
            **Ejemplo**: Si ves muchos puntos rojos a la derecha en `log_subscribers`, 
            significa que más suscriptores generalmente aumentan el engagement predicho.
            """)
        else:
            st.warning("Imágenes SHAP no encontradas. Ejecuta el notebook de entrenamiento para generarlas.")
            st.info("Puedes encontrar el notebook en: `03_Modelo_XGBoost_LightGBM/youtube_xgboost_predictor.ipynb`")
    
    # ===== TAB 4: Matriz de Confusión =====
    with tab4:
        st.markdown("### 📊 Matriz de Confusión (LightGBM Classifier)")
        st.markdown("Muestra cómo se distribuyen las predicciones vs realidad:")
        
        # Cargar imagen de matriz de confusión
        confusion_path = Path("../03_Modelo_XGBoost_LightGBM/confusion_matrix.png")
        
        if confusion_path.exists():
            st.image(str(confusion_path), 
                    caption="Matriz de Confusión - Clasificación de Engagement",
                    use_container_width=True)
            
            st.markdown("""
            #### 📖 Interpretación
            
            - **Diagonal principal**: Predicciones correctas
            - **Fuera de diagonal**: Errores de clasificación
            - **Categorías**: Bajo (<2%), Medio (2-5%), Alto (5-10%), Viral (>10%)
            
            El modelo tiene mejor desempeño en las categorías extremas (Bajo y Viral) 
            y más dificultad diferenciando entre Medio y Alto.
            """)
            
            # Estadísticas adicionales si están disponibles
            if metrics_lgb and 'classification_report' in metrics_lgb:
                st.markdown("#### 📋 Reporte de Clasificación Detallado")
                st.json(metrics_lgb['classification_report'])
        else:
            st.warning("Matriz de confusión no encontrada. Ejecuta el notebook de entrenamiento para generarla.")

except Exception as e:
    st.error(f"Error al cargar el dashboard: {str(e)}")
    st.info("""
    **Posibles soluciones:**
    1. Verifica que los modelos estén entrenados en `03_Modelo_XGBoost_LightGBM/`
    2. Ejecuta el notebook `youtube_xgboost_predictor.ipynb` para generar los modelos
    3. Asegúrate de que las rutas relativas sean correctas
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard actualizado con los últimos modelos entrenados</p>
</div>
""", unsafe_allow_html=True)
