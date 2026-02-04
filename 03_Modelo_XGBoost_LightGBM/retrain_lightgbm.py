"""
Script para re-entrenar el modelo LightGBM correctamente
Predice categorías de ENGAGEMENT (Bajo, Medio, Alto, Viral), no categorías de YouTube
"""

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print("RE-ENTRENAMIENTO DE LIGHTGBM - CLASIFICADOR DE ENGAGEMENT")
print("=" * 80)

# 1. CARGAR DATASET ACTUALIZADO
print("\n📂 Cargando dataset actualizado...")
df = pd.read_csv('../datasets/dataset_ML_food.csv')
print(f"✓ Dataset cargado: {len(df)} registros")

# 2. CALCULAR ENGAGEMENT RATE
print("\n📊 Calculando engagement rate...")
df['engagement_rate'] = ((df['like_count'] + 50 * df['comment_count']) / df['view_count'] * 100)
df = df[df['engagement_rate'].notna() & (df['engagement_rate'] > 0)]
print(f"✓ Engagement rate calculado para {len(df)} registros válidos")

# 3. CREAR CATEGORÍAS DE ENGAGEMENT (LO QUE FALTABA!)
print("\n🏷️ Creando categorías de engagement...")
def categorize_engagement(rate):
    if rate < 2:
        return 'Bajo'
    elif rate < 5:
        return 'Medio'
    elif rate < 10:
        return 'Alto'
    else:
        return 'Viral'

df['engagement_category'] = df['engagement_rate'].apply(categorize_engagement)

# Mostrar distribución
print("\nDistribución de categorías:")
print(df['engagement_category'].value_counts().sort_index())
print(f"\nPorcentajes:")
print((df['engagement_category'].value_counts(normalize=True) * 100).sort_index())

# 4. CARGAR SCALER Y FEATURE NAMES
print("\n📦 Cargando scaler y features...")
scaler = joblib.load('scaler_xgb.pkl')
feature_names = list(scaler.feature_names_in_)
print(f"✓ {len(feature_names)} features a usar")

# 5. PREPARAR DATOS
print("\n🔧 Preparando features...")

# Seleccionar solo las columnas que existen en el dataset
available_features = [f for f in feature_names if f in df.columns]
missing_features = set(feature_names) - set(available_features)

print(f"✓ Features disponibles: {len(available_features)}")
if missing_features:
    print(f"⚠️ Features faltantes: {missing_features}")
    print("   Se rellenarán con 0")

# Crear X con todas las features necesarias
X = df[available_features].copy()

# Añadir features faltantes con valor 0
for feat in missing_features:
    X[feat] = 0

# Reordenar según el orden del scaler
X = X[feature_names]

# Variable target
y = df['engagement_category']

print(f"\n✓ X shape: {X.shape}")
print(f"✓ y shape: {y.shape}")

# 6. CODIFICAR TARGET
print("\n🔢 Codificando categorías...")
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print(f"✓ Clases: {le.classes_}")
print(f"✓ Mapeo: {dict(enumerate(le.classes_))}")

# 7. SPLIT TRAIN/TEST
print("\n✂️ Dividiendo datos...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"✓ Train: {len(X_train)} | Test: {len(X_test)}")

# 8. ESCALAR FEATURES
print("\n⚖️ Escalando features...")
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✓ Features escaladas")

# 9. ENTRENAR LIGHTGBM
print("\n🚀 Entrenando LightGBM Classifier...")
lgb_model = lgb.LGBMClassifier(
    objective='multiclass',
    num_class=len(le.classes_),
    n_estimators=200,
    learning_rate=0.05,
    max_depth=7,
    num_leaves=31,
    min_child_samples=20,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1
)

lgb_model.fit(X_train_scaled, y_train)
print("✓ Modelo entrenado")

# 10. EVALUAR MODELO
print("\n📈 Evaluando modelo...")
y_pred_train = lgb_model.predict(X_train_scaled)
y_pred_test = lgb_model.predict(X_test_scaled)

train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print(f"\n✓ Accuracy Train: {train_acc:.4f} ({train_acc*100:.2f}%)")
print(f"✓ Accuracy Test: {test_acc:.4f} ({test_acc*100:.2f}%)")

# Classification Report
print("\n📊 Classification Report (Test):")
print(classification_report(y_test, y_pred_test, target_names=le.classes_))

# 11. GUARDAR MODELO Y ENCODER
print("\n💾 Guardando modelo y label encoder...")
joblib.dump(lgb_model, 'lightgbm_engagement_classifier.pkl')
joblib.dump(le, 'label_encoder_engagement.pkl')
print("✓ Modelo guardado: lightgbm_engagement_classifier.pkl")
print("✓ Label Encoder guardado: label_encoder_engagement.pkl")

# 12. GUARDAR MÉTRICAS
metrics = {
    'model_type': 'LightGBM Classifier (ENGAGEMENT)',
    'train': {
        'accuracy': float(train_acc)
    },
    'test': {
        'accuracy': float(test_acc),
    },
    'classes': le.classes_.tolist(),
    'class_distribution': df['engagement_category'].value_counts().to_dict(),
    'n_features': len(feature_names),
    'n_samples_train': int(len(X_train)),
    'n_samples_test': int(len(X_test))
}

with open('lightgbm_classification_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)
print("✓ Métricas guardadas: lightgbm_classification_metrics.json")

# 13. MATRIZ DE CONFUSIÓN
print("\n📊 Generando matriz de confusión...")
cm = confusion_matrix(y_test, y_pred_test)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title('Matriz de Confusión - LightGBM Classifier (Engagement)')
plt.ylabel('Real')
plt.xlabel('Predicho')
plt.tight_layout()
plt.savefig('confusion_matrix_lightgbm.png', dpi=300, bbox_inches='tight')
print("✓ Matriz guardada: confusion_matrix_lightgbm.png")

# 14. FEATURE IMPORTANCE
print("\n🎯 Generando feature importance...")
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': lgb_model.feature_importances_
}).sort_values('importance', ascending=False)

plt.figure(figsize=(12, 8))
top_20 = importance_df.head(20)
plt.barh(range(len(top_20)), top_20['importance'])
plt.yticks(range(len(top_20)), top_20['feature'])
plt.xlabel('Importance')
plt.title('Top 20 Feature Importance - LightGBM Classifier')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('feature_importance_lightgbm.png', dpi=300, bbox_inches='tight')
print("✓ Feature importance guardada: feature_importance_lightgbm.png")

print("\n" + "=" * 80)
print("✅ RE-ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
print("=" * 80)
print(f"\n🎯 Modelo CORREGIDO - Predice: {', '.join(le.classes_)}")
print(f"📊 Accuracy: {test_acc*100:.2f}%")
print(f"📁 Archivos generados:")
print("   - lightgbm_engagement_classifier.pkl")
print("   - label_encoder_engagement.pkl")
print("   - lightgbm_classification_metrics.json")
print("   - confusion_matrix_lightgbm.png")
print("   - feature_importance_lightgbm.png")
