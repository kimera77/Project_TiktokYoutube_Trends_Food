"""
Aplicación Streamlit Multi-Página para Predicción de Engagement en YouTube
Proyecto: TikTok/YouTube Trends Food - Machine Learning
"""

import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="YouTube ML Predictor",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Página principal (Home)
st.title("🎥 YouTube Food Engagement Predictor")
st.markdown("### Predice el engagement de tus videos de comida usando Machine Learning")

st.markdown("""
---

## 👋 Bienvenido

Esta aplicación utiliza modelos de **XGBoost** y **LightGBM** entrenados con miles de videos de comida
para predecir el engagement que obtendrá tu video en YouTube.

### 🎯 ¿Qué puedes hacer aquí?

""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📊 Dashboard
    
    - **Métricas del modelo** (R², MAE, RMSE)
    - **Importancia de características**
    - **Matriz de confusión**
    - **Análisis SHAP** de interpretabilidad
    - **Distribución de predicciones**
    
    → Visualiza cómo funcionan los modelos
    """)

with col2:
    st.markdown("""
    #### 🎯 Predictor
    
    - **Predicción de engagement rate**
    - **Clasificación** (Bajo/Medio/Alto/Viral)
    - **Métricas esperadas** (likes, comentarios)
    - **Análisis de características** de tu video
    - **Confianza de la predicción**
    
    → Predice el rendimiento de tu video
    """)

with col3:
    st.markdown("""
    #### 💡 Optimizador
    
    - **Recomendaciones personalizadas**
    - **Análisis de título** y palabras clave
    - **Optimización de timing**
    - **Sugerencias de contenido**
    - **Exportación de resultados**
    
    → Mejora tu video antes de publicarlo
    """)

st.markdown("---")

st.markdown("""
### 📈 Sobre los Modelos

Los modelos han sido entrenados con **5,682 videos** de comida en YouTube, utilizando:

- **35+ características** extraídas (sentiment, título, temporales, canal, contenido)
- **XGBoost Regressor** para predecir engagement rate (R² = 0.0726)
- **LightGBM Classifier** para categorizar engagement (Accuracy = 43.9%)
- **SHAP values** para interpretabilidad de predicciones

### 🚀 Comienza Ahora

**👈 Selecciona una página en el menú lateral** para comenzar a explorar.

""")

st.info("""
💡 **Tip**: Para mejores resultados, asegúrate de completar todos los campos del formulario.
Los campos obligatorios están marcados con un asterisco (*).
""")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Desarrollado con ❤️ usando Streamlit + XGBoost + LightGBM</p>
    <p>Proyecto TikTok/YouTube Trends Food | 2025</p>
</div>
""", unsafe_allow_html=True)
