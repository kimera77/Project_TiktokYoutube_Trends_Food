# 🎥 YouTube Trends Food - Proyecto de Machine Learning

## 📁 Estructura del Proyecto

```
Project_TiktokYoutube_Trends_Food/
│
├── 01_ETL_PowerBI/                    # ETL y Visualización PowerBI
│   ├── POWERBI_ETL2025.ipynb          # Notebook ETL para PowerBI
│   ├── YouTtiktok_powerBI.pbix        # Dashboard PowerBI
│   ├── DATA_DICTIONARY.csv            # Diccionario de datos
│   ├── README_ETL.md                  # Documentación del ETL
│   └── README_PowerBI.md              # Documentación PowerBI
│
├── 02_Modelo_Keras_DeepLearning/      # Modelo Deep Learning (Multi-Output)
│   ├── youtube_ml_predictor.ipynb     # Notebook principal del modelo Keras
│   ├── best_model.keras               # Mejor modelo guardado (checkpoint)
│   ├── youtube_predictor_final.keras  # Modelo final entrenado
│   ├── scaler.pkl                     # StandardScaler para normalización
│   ├── title_embeddings.npy           # Embeddings pre-calculados
│   ├── model_config.txt               # Configuración del modelo
│   ├── model_metrics.json             # Métricas de evaluación
│   └── deepLearning_predictor.md      # Documentación del modelo
│
├── 03_Modelo_XGBoost_LightGBM/        # Modelo Ensemble (Regresión + Clasificación)
│   ├── youtube_xgboost_predictor.ipynb           # Notebook principal XGBoost/LightGBM
│   ├── xgboost_engagement_regressor.pkl          # Modelo XGBoost (regresión)
│   ├── lightgbm_engagement_classifier.pkl        # Modelo LightGBM (clasificación)
│   ├── scaler_xgb.pkl                            # StandardScaler para XGBoost
│   ├── label_encoder_category.pkl                # Encoder para categorías
│   ├── label_encoder_language.pkl                # Encoder para idiomas
│   ├── xgboost_regression_metrics.json           # Métricas del modelo de regresión
│   ├── lightgbm_classification_metrics.json      # Métricas del modelo de clasificación
│   ├── feature_importance_xgboost.png            # Gráfico de importancia (XGBoost)
│   ├── feature_importance_lightgbm.png           # Gráfico de importancia (LightGBM)
│   ├── confusion_matrix_lightgbm.png             # Matriz de confusión
│   ├── xgboost_regression_results.png            # Resultados de predicción
│   ├── shap_summary_bar.png                      # SHAP values (barra)
│   └── shap_summary_dot.png                      # SHAP values (puntos)
│
├── datasets/                          # Datasets CSV + Script de extracción
│   ├── getDataset_youtubeML.py        # Script para obtener datos de YouTube API
│   ├── dataset_ML_food.csv            # Dataset principal para ML
│   ├── dataset_ML_food - copia.csv    # Backup del dataset
│   └── food_videos_2025_clean.csv     # Dataset limpio de videos 2025
│
├── EvidenciasPowerBI/                 # Evidencias y screenshots de PowerBI
├── venv/                              # Entorno virtual de Python
├── .env                               # Variables de entorno (API Keys)
├── .gitignore                         # Archivos ignorados por Git
└── Memoria Técnica.docx               # Memoria técnica del proyecto
```

---

## 🎯 Descripción de los Modelos

### **Modelo 1: Keras Deep Learning** (02_Modelo_Keras_DeepLearning/)
- **Tipo:** Red Neuronal Multi-Output
- **Target:** Predicción simultánea de `views`, `likes`, `comments`
- **Features:** Embeddings de títulos (SentenceTransformer) + features numéricas
- **Arquitectura:** Dense layers + Dropout + Batch Normalization
- **Resultados:** R² muy bajo (~0-0.03), no apto para producción

### **Modelo 2: XGBoost/LightGBM Ensemble** (03_Modelo_XGBoost_LightGBM/)
- **Tipo:** Ensemble (Gradient Boosting)
- **Target:** 
  - Regresión: `engagement_rate`
  - Clasificación: Nivel de éxito (Bajo/Medio/Alto/Viral)
- **Features:** 35+ features engineered (sentiment, temporal, canal, contenido)
- **Interpretabilidad:** Feature importance + SHAP values
- **Resultados:** R² = 0.0726, Accuracy = 43.9% (mejor que Keras)

---

## 🚀 Cómo Usar

### 1. **Obtener datos de YouTube API** (Actualización diaria)
```bash
cd datasets
python getDataset_youtubeML.py
```

### 2. **Entrenar modelo Keras**
Abrir `02_Modelo_Keras_DeepLearning/youtube_ml_predictor.ipynb` y ejecutar todas las celdas.

### 3. **Entrenar modelo XGBoost**
Abrir `03_Modelo_XGBoost_LightGBM/youtube_xgboost_predictor.ipynb` y ejecutar todas las celdas.

---

## 📊 Datasets

Todos los datasets CSV están en la carpeta `datasets/`:
- **dataset_ML_food.csv**: Dataset principal con 6,457 videos de comida
- Columnas: `video_id`, `title`, `view_count`, `like_count`, `comment_count`, etc.

---

## 🔧 Requisitos

```bash
pip install tensorflow pandas numpy scikit-learn xgboost lightgbm shap matplotlib seaborn sentence-transformers vaderSentiment textblob joblib
```

---

## 📝 Notas

- Las rutas en los notebooks son **relativas** a la carpeta del notebook
- Los datasets siempre se cargan desde `../datasets/`
- Los modelos se guardan en su carpeta correspondiente
- Para actualizar datos: ejecutar `python getDataset_youtubeML.py` desde `datasets/`

---

## 👤 Autor
Joaquim - Proyecto de Machine Learning para predicción de engagement en YouTube
