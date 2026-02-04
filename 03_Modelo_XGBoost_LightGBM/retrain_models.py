"""
Script para re-entrenar modelos XGBoost y LightGBM con datos actualizados
Corrige el problema del label_encoder incorrecto
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score
import xgboost as xgb
import lightgbm as lgb
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔄 RE-ENTRENAMIENTO DE MODELOS - XGBoost & LightGBM")
print("=" * 80)

# 1. CARGAR DATOS ACTUALIZADOS
print("\n📂 Cargando dataset actualizado...")
df = pd.read_csv('../datasets/dataset_ML_food.csv')
print(f"✓ Dataset cargado: {len(df)} registros")

# 2. CALCULAR ENGAGEMENT RATE
print("\n📊 Calculando engagement rate...")
df['engagement_rate'] = ((df['like_count'] + 50 * df['comment_count']) / df['view_count']) * 100
df['engagement_rate'] = df['engagement_rate'].clip(0, 100)  # Limitar a 0-100%
print(f"✓ Engagement rate calculado (rango: {df['engagement_rate'].min():.2f}% - {df['engagement_rate'].max():.2f}%)")

# 3. CREAR CATEGORÍAS DE ENGAGEMENT (LO QUE FALTABA!)
print("\n🏷️  Creando categorías de engagement...")
def categorize_engagement(rate):
    if rate < 2:
        return 0  # Bajo
    elif rate < 5:
        return 1  # Medio
    elif rate < 10:
        return 2  # Alto
    else:
        return 3  # Viral

df['engagement_category'] = df['engagement_rate'].apply(categorize_engagement)

# Crear el label encoder CORRECTO para engagement
le_engagement = LabelEncoder()
le_engagement.fit([0, 1, 2, 3])  # Asegurar orden correcto
le_engagement.classes_ = np.array(['Bajo', 'Medio', 'Alto', 'Viral'])

print(f"✓ Categorías creadas:")
for i, cat in enumerate(le_engagement.classes_):
    count = len(df[df['engagement_category'] == i])
    pct = (count / len(df)) * 100
    print(f"   {i} - {cat}: {count} videos ({pct:.1f}%)")

# 4. PREPARAR FEATURES
print("\n🔧 Preparando features...")

# Cargar el scaler existente para saber qué features necesitamos
scaler_original = joblib.load('scaler_xgb.pkl')
feature_names = list(scaler_original.feature_names_in_)
print(f"✓ Se necesitan {len(feature_names)} features")

# Seleccionar solo las features que existen en el dataset
available_features = [f for f in feature_names if f in df.columns]
print(f"✓ Features disponibles en el dataset: {len(available_features)}")

if len(available_features) < len(feature_names):
    print(f"⚠️  Faltan {len(feature_names) - len(available_features)} features")
    missing = set(feature_names) - set(available_features)
    print(f"   Features faltantes: {missing}")

# Usar las features disponibles
X = df[available_features].copy()
y_regression = df['engagement_rate'].copy()
y_classification = df['engagement_category'].copy()

# 5. SPLIT TRAIN/TEST
print("\n✂️  Dividiendo train/test (80/20)...")
X_train, X_test, y_train_reg, y_test_reg = train_test_split(
    X, y_regression, test_size=0.2, random_state=42
)
_, _, y_train_clf, y_test_clf = train_test_split(
    X, y_classification, test_size=0.2, random_state=42
)
print(f"✓ Train: {len(X_train)} | Test: {len(X_test)}")

# 6. ESCALAR DATOS
print("\n📏 Escalando datos...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✓ Datos escalados")

# 7. ENTRENAR XGBOOST (REGRESIÓN)
print("\n" + "=" * 80)
print("🔵 ENTRENANDO XGBOOST REGRESSOR (Engagement Rate)")
print("=" * 80)

xgb_params = {
    'objective': 'reg:squarederror',
    'max_depth': 6,
    'learning_rate': 0.05,
    'n_estimators': 200,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'n_jobs': -1
}

xgb_reg = xgb.XGBRegressor(**xgb_params)
xgb_reg.fit(X_train_scaled, y_train_reg, verbose=False)

# Evaluar XGBoost
y_pred_train = xgb_reg.predict(X_train_scaled)
y_pred_test = xgb_reg.predict(X_test_scaled)

r2_train = r2_score(y_train_reg, y_pred_train)
r2_test = r2_score(y_test_reg, y_pred_test)
mae_test = mean_absolute_error(y_test_reg, y_pred_test)
rmse_test = np.sqrt(mean_squared_error(y_test_reg, y_pred_test))

print(f"\n📊 Métricas XGBoost:")
print(f"   R² Train: {r2_train:.4f}")
print(f"   R² Test:  {r2_test:.4f}")
print(f"   MAE Test: {mae_test:.4f}")
print(f"   RMSE Test: {rmse_test:.4f}")

# 8. ENTRENAR LIGHTGBM (CLASIFICACIÓN)
print("\n" + "=" * 80)
print("🟢 ENTRENANDO LIGHTGBM CLASSIFIER (Categoría de Engagement)")
print("=" * 80)

lgb_params = {
    'objective': 'multiclass',
    'num_class': 4,
    'metric': 'multi_logloss',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'n_estimators': 200,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'n_jobs': -1,
    'verbose': -1
}

lgb_clf = lgb.LGBMClassifier(**lgb_params)
lgb_clf.fit(X_train_scaled, y_train_clf)

# Evaluar LightGBM
y_pred_train_clf = lgb_clf.predict(X_train_scaled)
y_pred_test_clf = lgb_clf.predict(X_test_scaled)

acc_train = accuracy_score(y_train_clf, y_pred_train_clf)
acc_test = accuracy_score(y_test_clf, y_pred_test_clf)
f1_macro = f1_score(y_test_clf, y_pred_test_clf, average='macro')
f1_weighted = f1_score(y_test_clf, y_pred_test_clf, average='weighted')

print(f"\n📊 Métricas LightGBM:")
print(f"   Accuracy Train: {acc_train:.4f}")
print(f"   Accuracy Test:  {acc_test:.4f}")
print(f"   F1-Score (Macro): {f1_macro:.4f}")
print(f"   F1-Score (Weighted): {f1_weighted:.4f}")

# 9. GUARDAR MODELOS Y METADATA
print("\n" + "=" * 80)
print("💾 GUARDANDO MODELOS Y CONFIGURACIÓN")
print("=" * 80)

# Guardar modelos
joblib.dump(xgb_reg, 'xgboost_engagement_regressor.pkl')
print("✓ xgboost_engagement_regressor.pkl")

joblib.dump(lgb_clf, 'lightgbm_engagement_classifier.pkl')
print("✓ lightgbm_engagement_classifier.pkl")

# Guardar scaler
joblib.dump(scaler, 'scaler_xgb.pkl')
print("✓ scaler_xgb.pkl")

# Guardar label encoder CORRECTO
joblib.dump(le_engagement, 'label_encoder_category.pkl')
print("✓ label_encoder_category.pkl (CORREGIDO - ahora tiene Bajo/Medio/Alto/Viral)")

# Guardar métricas
xgb_metrics = {
    'model_type': 'XGBoost Regressor',
    'train': {'r2': r2_train},
    'test': {'r2': r2_test, 'mae': mae_test, 'rmse': rmse_test},
    'n_features': len(available_features),
    'n_samples_train': len(X_train),
    'n_samples_test': len(X_test)
}

lgb_metrics = {
    'model_type': 'LightGBM Classifier',
    'train': {'accuracy': acc_train},
    'test': {'accuracy': acc_test, 'f1_macro': f1_macro, 'f1_weighted': f1_weighted},
    'n_features': len(available_features),
    'n_samples_train': len(X_train),
    'n_samples_test': len(X_test)
}

with open('xgboost_regression_metrics.json', 'w') as f:
    json.dump(xgb_metrics, f, indent=2)
print("✓ xgboost_regression_metrics.json")

with open('lightgbm_classification_metrics.json', 'w') as f:
    json.dump(lgb_metrics, f, indent=2)
print("✓ lightgbm_classification_metrics.json")

print("\n" + "=" * 80)
print("✅ RE-ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
print("=" * 80)
print(f"\n📈 Resumen:")
print(f"   Dataset: {len(df)} videos")
print(f"   Features: {len(available_features)}")
print(f"   XGBoost R²: {r2_test:.4f}")
print(f"   LightGBM Accuracy: {acc_test:.4f}")
print(f"\n🔧 Cambio crítico:")
print(f"   label_encoder_category.pkl ahora codifica: {list(le_engagement.classes_)}")
print(f"   (Antes codificaba categorías de YouTube incorrectamente)")
print("\n💡 Siguiente paso:")
print(f"   Reinicia Streamlit para que cargue los nuevos modelos")
