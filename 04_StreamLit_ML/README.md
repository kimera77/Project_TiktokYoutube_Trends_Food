# 🎥 YouTube Food Engagement Predictor - Streamlit App

Aplicación web interactiva para predecir y optimizar el engagement de videos de comida en YouTube usando Machine Learning.

## 📋 Descripción

Esta aplicación multi-página permite:
- **Visualizar** el rendimiento de los modelos ML entrenados
- **Predecir** el engagement rate y categoría de videos nuevos
- **Optimizar** videos con recomendaciones personalizadas basadas en reglas

## ✨ Características Destacadas

### 💾 Persistencia de Datos
Los datos ingresados en el **Predictor** se mantienen guardados automáticamente:
- Los campos del formulario conservan sus valores aunque cambies de página
- Puedes navegar entre Dashboard, Predictor y Optimizador sin perder información
- Usa el botón "🔄 Limpiar Formulario" para empezar desde cero
- Los valores se almacenan en `st.session_state` durante toda la sesión

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Verificar Modelos Entrenados

Asegúrate de que existan los siguientes archivos en `../03_Modelo_XGBoost_LightGBM/`:

- `xgboost_regressor.pkl`
- `lightgbm_classifier.pkl`
- `scaler_xgb.pkl`
- `label_encoder_lgb.pkl`
- `feature_names.pkl`
- `xgb_metrics.json`
- `lgb_metrics.json`

Si no existen, ejecuta el notebook `../03_Modelo_XGBoost_LightGBM/youtube_xgboost_predictor.ipynb`

### 3. Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📂 Estructura de Archivos

```
04_StreamLit_ML/
│
├── app.py                          # Página principal (Home)
├── pages/
│   ├── 1_📊_Dashboard.py          # Visualizaciones del modelo
│   ├── 2_🎯_Predictor.py          # Formulario de predicción
│   └── 3_💡_Optimizador.py        # Recomendaciones de mejora
│
├── utils.py                        # Funciones de feature engineering
├── predictor.py                    # Lógica de predicción con modelos
├── optimizer.py                    # Generador de recomendaciones
│
├── requirements.txt                # Dependencias de Python
├── README.md                       # Este archivo
└── PLAN.md                         # Documento de planificación original
```

## 🎯 Uso de las Páginas

### 📊 Dashboard

Visualiza:
- Métricas de rendimiento (R², MAE, RMSE, Accuracy)
- Importancia de características (top 15)
- Análisis SHAP de interpretabilidad
- Matriz de confusión del clasificador

### 🎯 Predictor

1. Completa el formulario con información de tu video:
   - **Obligatorios**: Título, Suscriptores, Duración, Vistas esperadas, Fecha/Hora publicación
   - **Opcionales**: Tags, Descripción

2. Haz clic en "Predecir Engagement"

3. Visualiza:
   - Engagement rate predicho
   - Categoría (Bajo/Medio/Alto/Viral)
   - Probabilidades por categoría
   - Métricas esperadas (likes, comentarios)
   - Análisis de características

4. Exporta los resultados en JSON

### 💡 Optimizador

Después de hacer una predicción:

1. Ve automáticamente al optimizador (o navega manualmente)

2. Revisa recomendaciones organizadas por:
   - 🚨 **Problemas Críticos**: Deben corregirse
   - ⚠️ **Advertencias**: Mejoras importantes
   - 💡 **Sugerencias**: Optimizaciones adicionales
   - ✅ **Aspectos Positivos**: Elementos bien optimizados

3. Ve tu puntuación de optimización (0-100)

4. Exporta el reporte completo en TXT

## 🔧 Características Técnicas

### Feature Engineering

La aplicación extrae **35+ características**:

- **Sentiment** (4): pos, neg, neu, compound (VADER)
- **Título** (8): longitud, palabras, mayúsculas, caracteres especiales, números, emojis, preguntas, exclamaciones
- **Temporal** (9): hora, día semana, día mes, mes, año, es fin de semana, es hora pico, días desde publicación
- **Canal** (2): suscriptores, log(suscriptores)
- **Contenido** (10): duración, log(duración), minutos, categoría duración, tags, descripción

### Modelos

- **XGBoost Regressor**: Predice engagement rate continuo (R² = 0.0726)
- **LightGBM Classifier**: Clasifica en categorías (Accuracy = 43.9%)

### Optimizador Basado en Reglas

Analiza:
- Longitud y contenido del título (30-70 caracteres óptimo)
- Palabras clave efectivas (receta, fácil, rápido, etc.)
- Timing de publicación (horas pico: 8-10, 12-14, 18-22)
- Duración del video (3-10 minutos óptimo)
- Cantidad de tags (5-15 recomendado)
- Descripción (50-200 palabras)

## 📊 Interpretación de Resultados

### Engagement Rate

- **< 2%**: Bajo engagement
- **2-5%**: Engagement medio
- **5-10%**: Alto engagement
- **> 10%**: Potencial viral

Fórmula: `engagement_rate = (likes + 50*comments) / views * 100`

### Confianza de Predicción

- **Alta**: Probabilidad máxima > 60%
- **Media**: Probabilidad máxima 40-60%
- **Baja**: Probabilidad máxima < 40%

### Puntuación de Optimización

- **80-100**: Video bien optimizado, listo para publicar
- **60-79**: Bueno, pero con margen de mejora
- **< 60**: Requiere optimización antes de publicar

## 🐛 Solución de Problemas

### Error: "Modelos no encontrados"

1. Verifica que existan los archivos `.pkl` en `../03_Modelo_XGBoost_LightGBM/`
2. Ejecuta el notebook de entrenamiento para generarlos

### Error: "Imágenes SHAP/Confusion no encontradas"

Las visualizaciones se generan durante el entrenamiento. Si no existen, el dashboard funcionará pero sin esas imágenes.

### Error: "ModuleNotFoundError"

Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Predicción da resultados extraños

- Verifica que los valores de entrada sean razonables
- El engagement rate típico está entre 1-15%
- Si obtienes valores fuera de rango, revisa los datos de entrada

## 📝 Notas Importantes

- La predicción es **orientativa**, no garantizada
- Los modelos tienen R² bajo (~0.07) debido a la complejidad inherente del engagement
- Factores externos (miniatura, thumbnail, algoritmo de YouTube) no se consideran
- Usa las recomendaciones como guía, no como reglas absolutas

## 🔄 Actualizaciones Futuras

Posibles mejoras:
- [ ] Análisis de miniaturas con Computer Vision
- [ ] Integración con YouTube API para datos en tiempo real
- [ ] Modelo de deep learning con embeddings más sofisticados
- [ ] Sistema de feedback para mejorar predicciones
- [ ] Comparación con videos similares exitosos

## 📧 Soporte

Si encuentras problemas:
1. Verifica que todos los archivos estén en su lugar
2. Revisa los logs de Streamlit en la terminal
3. Asegúrate de que las rutas relativas sean correctas

## 📄 Licencia

Proyecto académico - TikTok/YouTube Trends Food Analysis 2025

---

**Desarrollado con ❤️ usando Streamlit + XGBoost + LightGBM**
