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
    
    /* Modificar el texto "app" para que sea más pequeño y agregar "Inicio" */
    [data-testid="stSidebarNav"] > div:first-child {
        font-size: 10px !important;
        color: #999 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    [data-testid="stSidebarNav"] > div:first-child::after {
        content: "🏠 Inicio";
        display: block;
        font-size: 21px !important;
        color: #000 !important;
        margin-top: 5px;
        text-transform: none;
        letter-spacing: normal;
    }
</style>
""", unsafe_allow_html=True)

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
    
    <p><strong>Objetivo:</strong> Regresión del engagement rate (valor continuo)</p>
    <p><strong>Output:</strong> Valor numérico (ej: 5.3%)</p>
    
    <p><strong>Métricas de rendimiento:</strong></p>
    <ul>
        <li><strong>R² = 0.0726</strong> (coeficiente de determinación: explica el 7.26% de la varianza)</li>
        <li><strong>MAE = 4.61</strong> (error absoluto medio en puntos porcentuales)</li>
        <li><strong>RMSE = 9.89</strong> (raíz del error cuadrático medio, penaliza outliers)</li>
    </ul>
    
    <p><strong>Arquitectura:</strong></p>
    <ul>
        <li><strong>Gradient Boosting:</strong> Técnica de ensamble que combina múltiples modelos débiles de forma secuencial. Cada nuevo modelo corrige los errores del anterior, mejorando progresivamente las predicciones.</li>
        <li><strong>Extreme Gradient Boosting (XGBoost):</strong> Implementación optimizada de gradient boosting. Añade regularización automática y paralelización para mejorar rendimiento y evitar overfitting.</li>
        <li><strong>Decision Trees como base learners:</strong> Cada iteración construye un árbol de decisión que aprende de los residuos (errores) del modelo anterior.</li>
        <li><strong>Regularización L1/L2:</strong> Penalización añadida a la función de pérdida para reducir la complejidad del modelo. L1 promueve sparsity (muchos pesos a 0), L2 reduce magnitud de pesos.</li>
        <li><strong>Stochastic Gradient Boosting:</strong> Usa submuestreo aleatorio de datos y features en cada iteración para mejorar generalización y reducir overfitting.</li>
        <li><strong>Early Stopping:</strong> Detiene el entrenamiento automáticamente cuando el modelo deja de mejorar en un validation set, evitando entrenar iteraciones innecesarias.</li>
    </ul>
    
    <p><strong>Aplicación:</strong> Predicción numérica del engagement esperado</p>
    </div>
    """, unsafe_allow_html=True)

with col_modelo2:
    st.markdown("""
    <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
    <h4 style='color: #388E3C; margin-top: 0;'>🟢 LightGBM Classifier</h4>
    
    <p><strong>Objetivo:</strong> Clasificación multiclase del nivel de engagement</p>
    <p><strong>Output:</strong> Categoría {Bajo, Medio, Alto, Viral} + probabilidades</p>
    
    <p><strong>Métricas de rendimiento:</strong></p>
    <ul>
        <li><strong>Accuracy = 43.9%</strong> (test set, 92.7% training → overfitting detectado)</li>
        <li><strong>F1-Score macro = 0.44</strong> (promedio armónico de precision/recall)</li>
        <li><strong>Precision por clase:</strong> Bajo (66%), Medio (40%), Alto (35%), Viral (28%)</li>
    </ul>
    
    <p><strong>Arquitectura:</strong></p>
    <ul>
        <li><strong>Light Gradient Boosting Machine:</strong> Variante de gradient boosting optimizada para grandes datasets. Más rápida que XGBoost gracias a técnicas de optimización avanzadas.</li>
        <li><strong>Histogram-based learning:</strong> Agrupa valores continuos en bins discretos (histogramas). Reduce coste computacional y memoria, acelerando significativamente el entrenamiento.</li>
        <li><strong>Leaf-wise growth:</strong> Estrategia de crecimiento del árbol que elige la hoja con mayor ganancia para dividir (vs. level-wise que crece por niveles). Más eficiente pero propenso a overfitting.</li>
        <li><strong>Class weight balancing:</strong> Ajusta la importancia de cada clase según su frecuencia. Da más peso a clases minoritarias (ej: Viral) para evitar sesgo hacia clases mayoritarias.</li>
        <li><strong>GOSS (Gradient-based One-Side Sampling):</strong> Muestrea instancias manteniendo las de mayor gradiente (más difíciles de predecir) y descartando aleatoriamente las fáciles, mejorando eficiencia.</li>
        <li><strong>EFB (Exclusive Feature Bundling):</strong> Agrupa features mutuamente exclusivas para reducir dimensionalidad sin perder información, acelerando entrenamiento.</li>
    </ul>
    
    <p><strong>Aplicación:</strong> Clasificación del nivel de éxito esperado</p>
    
    <p style='color: #d84315; margin-top: 10px;'><strong>⚠️ Nota:</strong> Gap significativo train-test indica memorización de patrones específicos del training set</p>
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
