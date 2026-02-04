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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Estilos CSS para aumentar el tamaño del sidebar
st.markdown("""
<style>
    /* Aumentar tamaño de textos en sidebar - MÁS AGRESIVO */
    [data-testid="stSidebar"] * {
        font-size: 21px !important;
    }
    [data-testid="stSidebar"] label {
        font-size: 21px !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        font-size: 21px !important;
    }
    [data-testid="stSidebar"] p {
        font-size: 21px !important;
    }
    [data-testid="stSidebar"] a {
        font-size: 21px !important;
    }
    [data-testid="stSidebar"] span {
        font-size: 21px !important;
    }
    section[data-testid="stSidebar"] {
        font-size: 21px !important;
    }
    
    /* Ocultar el título por defecto de la página principal */
    [data-testid="stSidebar"] a[href="/"] span {
        display: none;
    }
    [data-testid="stSidebar"] a[href="/"] span::after {
        content: "🏠 Inicio";
        display: inline;
    }
</style>
""", unsafe_allow_html=True)

# Personalizar título de la página en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏠 Inicio")
st.sidebar.markdown("Bienvenido al predictor de engagement")

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

Los modelos han sido entrenados con **8,047 videos** de comida en YouTube, utilizando **35+ características** extraídas.

""")

# Explicación clara de cada modelo
col_modelo1, col_modelo2 = st.columns(2)

with col_modelo1:
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3;'>
    <h4 style='color: #1976D2; margin-top: 0;'>🔵 XGBoost Regressor</h4>
    <p><strong>Uso:</strong> Predice el <strong>valor numérico</strong> del engagement rate</p>
    <p><strong>Salida:</strong> Un número (ej: 5.3%)</p>
    <p><strong>Rendimiento:</strong> R² = 0.0726, MAE = 4.61</p>
    <p><strong>¿Cuándo se usa?</strong> Cuando necesitas saber el <strong>engagement exacto</strong> esperado</p>
    </div>
    """, unsafe_allow_html=True)

with col_modelo2:
    st.markdown("""
    <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
    <h4 style='color: #388E3C; margin-top: 0;'>🟢 LightGBM Classifier</h4>
    <p><strong>Uso:</strong> Clasifica el nivel de <strong>éxito del video</strong></p>
    <p><strong>Salida:</strong> Una categoría (Bajo, Medio, Alto, Viral)</p>
    <p><strong>Rendimiento:</strong> Accuracy = 43.9%</p>
    <p><strong>¿Cuándo se usa?</strong> Cuando quieres saber si tendrás <strong>éxito o no</strong></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""

#### 🔄 ¿Cómo trabajan juntos?

Ambos modelos se ejecutan **de forma independiente** sobre los mismos datos:
1. **XGBoost** te dice: *"Tu video tendrá un engagement de 5.3%"* (predicción numérica)
2. **LightGBM** te dice: *"Tu video será de nivel Alto"* (clasificación) 

Ambas predicciones se complementan para darte una **visión completa** del rendimiento esperado.

---

""")

st.markdown("""
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
