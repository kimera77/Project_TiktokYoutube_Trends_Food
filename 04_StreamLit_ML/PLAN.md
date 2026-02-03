# 📊 Plan de Desarrollo - Streamlit ML App

## 🎯 Objetivo
Crear una aplicación interactiva en Streamlit para visualizar, usar y optimizar el modelo XGBoost/LightGBM de predicción de engagement en YouTube.

---

## 📋 Estructura de la Aplicación

### **Parte 1: Dashboard del Modelo (Visualizaciones)**
Mostrar características y rendimiento del modelo entrenado.

**Gráficas a incluir:**
1. **Feature Importance** (XGBoost)
   - Mostrar las 20 features más importantes
   - Usar imagen: `../03_Modelo_XGBoost_LightGBM/feature_importance_xgboost.png`

2. **Métricas del Modelo**
   - Card con R², MAE, RMSE, MAPE
   - Comparativa Keras vs XGBoost (tabla o gráfico de barras)
   - Fuente: `../03_Modelo_XGBoost_LightGBM/xgboost_regression_metrics.json`

3. **Matriz de Confusión** (Clasificador LightGBM)
   - Mostrar imagen: `../03_Modelo_XGBoost_LightGBM/confusion_matrix_lightgbm.png`
   - Accuracy, F1-score por categoría

4. **SHAP Values** (Interpretabilidad)
   - Imagen: `../03_Modelo_XGBoost_LightGBM/shap_summary_bar.png` o `shap_summary_dot.png`

**Disposición sugerida:**
- Usar `st.columns()` para layout en 2-3 columnas
- Tabs (`st.tabs()`) para separar: "Métricas" | "Feature Importance" | "SHAP" | "Confusión"

---

### **Parte 2: Predictor Interactivo**
Formulario donde el usuario ingresa características de un video futuro y obtiene predicción.

**Campos de entrada necesarios** (según el modelo):

#### **📝 Información del Video:**
1. **Título** (`text_input`)
   - Para calcular: sentiment, longitud, emojis, hashtags, etc.

2. **Descripción** (`text_area`, opcional)
   - Longitud de descripción

3. **Duración** (`number_input`)
   - En segundos (1-600 típicamente)
   - Detectar automáticamente: is_short, is_medium, is_long

4. **Tags** (`number_input`)
   - Número de tags (0-30)

#### **📺 Información del Canal:**
5. **Suscriptores del canal** (`number_input`)
   - Para calcular: channel_size_category, log_subscribers

6. **Categoría** (`selectbox`)
   - Opciones: Entertainment, Howto & Style, Science & Technology, etc.

#### **⏰ Timing de Publicación:**
7. **Hora de publicación** (`slider` 0-23)
   - Para calcular: is_prime_time, is_morning, is_afternoon

8. **Día de la semana** (`selectbox`)
   - Lunes-Domingo → 0-6
   - Para calcular: is_weekend

#### **🎬 Calidad del Video:**
9. **Definición** (`radio`)
   - HD / SD

10. **Tiene subtítulos** (`checkbox`)

11. **Idioma** (`selectbox`)
    - en, es, pt, fr, etc.

**Botón de predicción:**
```python
if st.button("🔮 Predecir Engagement", type="primary"):
    # Procesar datos
    # Cargar modelos
    # Predecir
    # Mostrar resultados
```

**Resultados a mostrar:**
- 🎯 **Engagement Rate predicho**: X.XX%
- 📊 **Categoría**: Bajo 😐 / Medio 👍 / Alto 🔥 / Viral 🚀
- 📈 **Probabilidades por categoría** (gráfico de barras)
- 🔍 **Top 5 factores influyentes** (SHAP values)
- 💡 **Recomendación**: Texto con consejos

---

### **Parte 3: Generador de Video Óptimo**
Sugerir características ideales para maximizar engagement.

**Opciones de implementación:**

#### **Opción A: Basado en Reglas del Modelo** (Sin IA externa)
- Usar feature importance para identificar factores clave
- Analizar distribución de datos de videos exitosos (engagement > 10%)
- Generar recomendaciones basadas en patrones:
  - "Publica en fin de semana entre 6PM-10PM"
  - "Usa títulos con emojis y entre 50-70 caracteres"
  - "Canales con 100k-1M subs tienen mejor engagement"
  - etc.

#### **Opción B: Generación con IA (Qwen/OpenAI/Anthropic)** ⚠️ REQUIERE API
- Usar modelo LLM para generar título optimizado
- Analizar tendencias actuales
- Sugerir tags relevantes
- Crear descripción atractiva

**Implementación sugerida (sin IA):**
```python
if st.button("✨ Generar Video Ideal", type="secondary"):
    st.subheader("📌 Recomendaciones para Máximo Engagement")
    
    # Basado en análisis del dataset
    st.markdown("""
    ### 🎯 Características Óptimas:
    
    **Título:**
    - Longitud: 50-70 caracteres
    - Incluir: Emojis 🔥😍 + Números + Signos de exclamación
    - Sentimiento: Positivo (compound > 0.5)
    - Palabras clave: "BEST", "EASY", "DELICIOUS"
    
    **Timing:**
    - Día: Sábado o Domingo
    - Hora: 19:00 - 21:00 (Prime Time)
    
    **Canal:**
    - Ideal: 500k - 5M suscriptores
    - Categoría: Entertainment
    
    **Contenido:**
    - Duración: 120-180 segundos (Shorts)
    - Calidad: HD
    - Subtítulos: Sí
    - Tags: 10-15 tags
    """)
    
    # Opcionalmente: generar ejemplo de título con lógica
```

---

## 🔧 Requisitos Técnicos

### **Librerías necesarias:**
```bash
pip install streamlit plotly pandas numpy joblib xgboost lightgbm scikit-learn vaderSentiment
```

### **Archivos que necesita la app:**
- Modelos:
  - `../03_Modelo_XGBoost_LightGBM/xgboost_engagement_regressor.pkl`
  - `../03_Modelo_XGBoost_LightGBM/lightgbm_engagement_classifier.pkl`
  - `../03_Modelo_XGBoost_LightGBM/scaler_xgb.pkl`
  - `../03_Modelo_XGBoost_LightGBM/label_encoder_category.pkl`
  - `../03_Modelo_XGBoost_LightGBM/label_encoder_language.pkl`

- Métricas:
  - `../03_Modelo_XGBoost_LightGBM/xgboost_regression_metrics.json`
  - `../03_Modelo_XGBoost_LightGBM/lightgbm_classification_metrics.json`
  - `../02_Modelo_Keras_DeepLearning/model_metrics.json` (para comparación)

- Imágenes:
  - `../03_Modelo_XGBoost_LightGBM/feature_importance_xgboost.png`
  - `../03_Modelo_XGBoost_LightGBM/confusion_matrix_lightgbm.png`
  - `../03_Modelo_XGBoost_LightGBM/shap_summary_bar.png`

### **Funciones a replicar del notebook:**
1. `get_sentiment_features(text)` - VADER sentiment
2. `extract_title_features(title)` - Features del título
3. `categorize_channel_size(subscribers)` - Categoría del canal
4. Feature engineering completo
5. Predicción con carga de modelos

---

## 📁 Estructura de Archivos

```
04_StreamLit_ML/
├── app.py                          # Aplicación principal Streamlit
├── utils.py                        # Funciones auxiliares (feature engineering)
├── predictor.py                    # Lógica de predicción
├── optimizer.py                    # Generador de recomendaciones
├── requirements.txt                # Dependencias
├── PLAN.md                         # Este documento
└── README.md                       # Documentación de uso
```

---

## ❓ Preguntas y Decisiones Pendientes

### 1. **Layout de la aplicación**
- ❓ ¿Prefieres **una sola página** con secciones (scrollable)?
- ❓ O **multi-página** con sidebar navigation?
  - Página 1: Dashboard
  - Página 2: Predictor
  - Página 3: Optimizador

**Recomendación:** Multi-página para mejor organización

---

### 2. **Parte 3: Generador de Video Óptimo**
- ❓ ¿Tienes acceso a API de **Qwen** o algún LLM (OpenAI, Claude)?
  - Si **SÍ**: Podemos usar IA para generar títulos creativos y análisis avanzado
  - Si **NO**: Usamos lógica basada en reglas del modelo (igualmente útil)

**Recomendación inicial:** Empezar con lógica de reglas, luego añadir IA como feature opcional

---

### 3. **Campos del formulario**
- ❓ ¿Quieres **todos** los campos listados arriba?
- ❓ O prefieres un formulario **simplificado** (solo 5-6 campos más importantes)?

Campos críticos mínimos:
- Título ✅
- Duración ✅
- Suscriptores ✅
- Hora de publicación ✅
- Día de semana ✅

---

### 4. **Visualizaciones adicionales**
- ❓ ¿Quieres gráficos **interactivos con Plotly**?
  - Ejemplo: Scatter plot de predicciones vs reales
  - Histogramas de engagement por categoría
- ❓ O solo mostrar las **imágenes PNG** ya generadas?

**Recomendación:** Combinar ambos (imágenes estáticas + algunos gráficos interactivos)

---

### 5. **Datos de ejemplo**
- ❓ ¿Incluir botón de "Cargar ejemplo" con datos pre-rellenados?
- Ejemplo bueno vs ejemplo malo

---

### 6. **Exportar predicciones**
- ❓ ¿Quieres que el usuario pueda **descargar** las predicciones (CSV/JSON)?
- ❓ O guardar historial de predicciones en la sesión?

---

## 🚀 Plan de Implementación (Orden sugerido)

1. ✅ Crear estructura de carpetas y PLAN.md
2. ⏳ Responder preguntas pendientes
3. ⏳ Crear `utils.py` con funciones de feature engineering
4. ⏳ Crear `predictor.py` con lógica de carga y predicción
5. ⏳ Crear `optimizer.py` con generador de recomendaciones
6. ⏳ Crear `app.py` estructura básica
7. ⏳ Implementar Parte 1: Dashboard
8. ⏳ Implementar Parte 2: Predictor
9. ⏳ Implementar Parte 3: Optimizador
10. ⏳ Testing y refinamiento
11. ⏳ Documentación final (README.md)

---

## 💡 Notas Importantes

- La app debe funcionar **offline** (sin conexión a internet) excepto si usamos IA externa
- Todos los modelos y datos ya están guardados localmente
- Streamlit recarga automáticamente al guardar cambios
- Para ejecutar: `streamlit run app.py` desde la carpeta `04_StreamLit_ML/`

---

## 🎨 Estilo Visual Sugerido

- Usar emoji en títulos para mejor UX
- Color scheme: Azul/Verde para métricas positivas, Naranja/Rojo para alertas
- Cards con `st.metric()` para mostrar números clave
- Gráficos con Plotly para interactividad
- Sidebar para configuración/navegación
- Footer con créditos y enlace al GitHub

---

**Fecha de creación:** 2026-02-03  
**Última actualización:** 2026-02-03  
**Estado:** 🟡 Esperando confirmación de decisiones
