# 🎯 YouTube Success Predictor - Estrategia Actualizada

## 📋 Cambios Clave en el Enfoque

### ✅ Nuevo Target (Multi-Output)
**Predecir 3 variables simultáneamente:**
1. **views** (visualizaciones)
2. **likes** (me gusta)
3. **comments** (comentarios)

### 🎯 Métrica de Éxito: Engagement
Después de la predicción, calculamos:

```python
engagement = (likes + 50*comments) / views * 100
```

**Interpretación:**
- **< 2%**: Pasable 😐 - No genera comunidad
- **3-7%**: Bueno 👍 - Cumple su función
- **> 10%**: Éxito Total 🚀 - Impulsa crecimiento

---

## 🏗️ Arquitectura del Modelo

### Multi-Output Neural Network

```
┌─────────────────────────────────────────┐
│        INPUT: Features + Embeddings     │
│    (Numeric: 22 + Embeddings: 384)     │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │  Dense (256)    │
        │  + BatchNorm    │
        │  + Dropout 0.3  │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  Dense (128)    │
        │  + BatchNorm    │
        │  + Dropout 0.3  │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  Dense (64)     │
        │  + Dropout 0.2  │
        └────────┬────────┘
                 │
        ┌────────▼────────────────────┐
        │   SHARED REPRESENTATION     │
        └─┬────────┬─────────┬────────┘
          │        │         │
    ┌─────▼──┐ ┌──▼────┐ ┌──▼────────┐
    │ Views  │ │ Likes │ │ Comments  │
    │ Branch │ │ Branch│ │  Branch   │
    │Dense 32│ │Dense32│ │ Dense 32  │
    └────┬───┘ └───┬───┘ └────┬──────┘
         │         │          │
    ┌────▼───┐ ┌──▼────┐ ┌───▼───────┐
    │Output 1│ │Output2│ │  Output 3 │
    │(linear)│ │(linear│ │  (linear) │
    └────────┘ └───────┘ └───────────┘
```

**Por qué este enfoque:**
1. **Aprendizaje compartido**: Las 3 métricas están correlacionadas
2. **Mejor generalización**: El modelo aprende patrones comunes
3. **Eficiencia**: Un solo modelo en vez de 3 separados

---

## 📂 Estructura de Archivos (SIMPLIFICADA)

```
proyecto_youtube/
│
├── youtube_ml_predictor.ipynb    # ← NOTEBOOK PRINCIPAL (todo-en-uno)
│
├── data/
│   └── dataset_ML_food_-_copia.csv
│
└── models/                        # Se genera automáticamente
    ├── youtube_predictor_final.keras
    ├── scaler.pkl
    ├── title_embeddings.npy
    ├── model_config.txt
    └── model_metrics.json
```

**Simplicidad:** Solo 1 notebook para todo el pipeline.

---

## 🔑 Features Usadas (NO views/likes/comments)

### 📝 Textuales
- `title_length`, `title_word_count`
- `title_emoji_count`, `title_hashtag_count`
- `title_uppercase_ratio`
- `title_sentiment` (VADER)
- `title_embeddings` (384 dims - Sentence-BERT)
- `desc_length`, `desc_word_count`
- `desc_has_link`, `desc_sentiment`

### ⏰ Temporales
- `publish_hour` (0-23)
- `publish_day_of_week` (0-6)
- `publish_month` (1-12)
- `is_weekend` (boolean)

### 📹 Contenido
- `duration_sec`
- `category_id`
- `tag_count`
- `caption_bool`, `licensed_bool`, `hd_bool`
- `made_for_kids`

### 📺 Canal
- `log_subscribers` (log transform de subscriber_count)

**TOTAL: ~406 features** (22 numéricas + 384 embeddings)

---

## ⚠️ Data Leakage Prevention

### ❌ NUNCA usar en features:
- `view_count`
- `like_count`
- `comment_count`
- `engagement_rate`
- `views_per_hour` ← **Eliminado** (depende de view_count)

### ✅ Solo metadatos disponibles ANTES de publicar:
- Título, descripción, tags
- Hora/día de publicación
- Duración, categoría
- Suscriptores del canal

---

## 📊 Flujo de Trabajo

### 1️⃣ EDA (Exploración)
- Distribución de views/likes/comments
- Análisis de engagement actual
- Detección de outliers
- Correlaciones

### 2️⃣ Feature Engineering
- Embeddings de título (Sentence-BERT)
- Análisis de sentimiento (VADER)
- Features temporales
- One-hot encoding de categorías

### 3️⃣ Modelado
- Log transform de targets (distribuciones sesgadas)
- Multi-Output Neural Network
- 3 losses simultáneas (MSE para cada output)
- Callbacks: EarlyStopping, ReduceLR, ModelCheckpoint

### 4️⃣ Evaluación
- MAE, RMSE, R² para cada output
- Scatter plots (predicho vs real)
- **Cálculo de engagement predicho**
- Clasificación de nivel de engagement

### 5️⃣ Predicción Nueva
```python
predict_new_video(video_metadata)
# → Devuelve: views, likes, comments, engagement, nivel
```

---

## 🎯 Función de Predicción

```python
nuevo_video = {
    'title': '🔥 Amazing Recipe! #viral',
    'description': 'Check this out!',
    'publish_hour': 18,
    'publish_day_of_week': 4,  # Viernes
    'tag_count': 5,
    'duration_sec': 45,
    'category_id': 22,
    'subscriber_count': 5000
}

resultado = predict_new_video(nuevo_video, model, scaler, embeddings_model)

# Output:
{
    'predicted_views': 3500,
    'predicted_likes': 120,
    'predicted_comments': 8,
    'predicted_engagement': 14.86,  # %
    'engagement_level': 'Éxito Total 🚀'
}
```

---

## 🧪 Métricas Esperadas (20k samples)

Con 20,000 registros, deberías obtener:

### Optimistas (buen dataset):
- **R² Views**: 0.70 - 0.85
- **R² Likes**: 0.65 - 0.80
- **R² Comments**: 0.60 - 0.75

### Realistas (dataset promedio):
- **R² Views**: 0.50 - 0.70
- **R² Likes**: 0.45 - 0.65
- **R² Comments**: 0.40 - 0.60

**Comments** suele ser el más difícil de predecir (más aleatorio).

---

## 💡 Mejoras Futuras

1. **Análisis de thumbnails** (CNN para extraer features visuales)
2. **Embeddings de descripción** (además del título)
3. **Features de competencia** (videos similares recientes)
4. **Análisis temporal avanzado** (tendencias por hora/día)
5. **Transfer Learning** (BERT fine-tuning si >50k datos)

---

## 🚀 Siguiente Paso

**Ejecuta el notebook** `youtube_ml_predictor.ipynb`:
1. Ajusta la ruta del CSV
2. Ejecuta celda por celda
3. Revisa las métricas
4. Prueba con videos nuevos

¡Todo listo para empezar! 🎉
