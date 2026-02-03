"""
Página de Predictor - Formulario interactivo para predecir engagement
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import create_features_from_input, format_engagement_category, calculate_expected_metrics
from predictor import VideoPredictor

st.set_page_config(page_title="Predictor", page_icon="🎯", layout="wide")

st.title("🎯 Predictor de Engagement")
st.markdown("### Predice el rendimiento de tu video antes de publicarlo")

# Inicializar predictor
@st.cache_resource
def load_predictor():
    return VideoPredictor(models_path="../03_Modelo_XGBoost_LightGBM")

try:
    predictor = load_predictor()
    
    # Formulario de input
    st.markdown("## 📝 Información del Video")
    st.markdown("*Campos obligatorios marcados con **")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📹 Datos Básicos")
            
            # Campo 1: Título (OBLIGATORIO)
            title = st.text_input(
                "Título del Video*",
                placeholder="Ej: 🍕 Cómo hacer la MEJOR pizza casera en 10 minutos",
                help="El título es crucial para el engagement. Incluye palabras clave atractivas."
            )
            
            # Campo 2: Suscriptores (OBLIGATORIO)
            subscriber_count = st.number_input(
                "Número de Suscriptores del Canal*",
                min_value=0,
                value=5000,
                step=100,
                help="Número total de suscriptores de tu canal"
            )
            
            # Campo 3: Duración (OBLIGATORIO)
            duration_minutes = st.number_input(
                "Duración (minutos)*",
                min_value=0.1,
                value=8.0,
                step=0.5,
                help="Duración total del video en minutos"
            )
            duration_seconds = int(duration_minutes * 60)
            
            # Campo 4: Vistas esperadas (OBLIGATORIO)
            expected_views = st.number_input(
                "Vistas Esperadas*",
                min_value=100,
                value=10000,
                step=500,
                help="Estimación de vistas basada en tu histórico o expectativa"
            )
            
            # Campo 5: Fecha de publicación (OBLIGATORIO)
            publish_date = st.date_input(
                "Fecha de Publicación Planeada*",
                value=datetime.now(),
                help="Cuándo planeas publicar el video"
            )
            
            publish_hour = st.slider(
                "Hora de Publicación*",
                min_value=0,
                max_value=23,
                value=18,
                help="Hora del día (formato 24h)"
            )
        
        with col2:
            st.markdown("### 🏷️ Información Adicional (Opcional)")
            
            # Campo 6: Tags (opcional)
            tags_input = st.text_area(
                "Tags del Video",
                placeholder="receta, cocina, pizza, facil, rapido, casero",
                help="Separa los tags con comas. Mejora el SEO del video."
            )
            
            # Campo 7: Descripción (opcional)
            description = st.text_area(
                "Descripción del Video",
                placeholder="Aprende a hacer la mejor pizza casera con ingredientes simples...",
                help="Una descripción detallada mejora el SEO y proporciona contexto"
            )
            
            st.markdown("---")
            st.info("""
            💡 **Tip**: Completa todos los campos opcionales para una predicción más precisa.
            La descripción y tags ayudan al algoritmo de YouTube a recomendar tu video.
            """)
        
        # Botón de submit
        submitted = st.form_submit_button("🔮 Predecir Engagement", use_container_width=True)
    
    # Procesamiento de la predicción
    if submitted:
        # Validar campos obligatorios
        if not title or len(title.strip()) < 5:
            st.error("❌ El título es obligatorio y debe tener al menos 5 caracteres")
        elif subscriber_count <= 0:
            st.error("❌ El número de suscriptores debe ser mayor a 0")
        elif duration_seconds <= 0:
            st.error("❌ La duración debe ser mayor a 0")
        elif expected_views <= 0:
            st.error("❌ Las vistas esperadas deben ser mayores a 0")
        else:
            # Crear datetime completo
            publish_datetime = datetime.combine(publish_date, datetime.min.time().replace(hour=publish_hour))
            
            with st.spinner("🔮 Realizando predicción..."):
                # Generar características
                features = create_features_from_input(
                    title=title,
                    subscriber_count=subscriber_count,
                    duration=duration_seconds,
                    publish_date=publish_datetime,
                    tags=tags_input,
                    description=description
                )
                
                # Guardar título en features para el optimizador
                features['title'] = title
                
                # Realizar predicción
                prediction_results = predictor.predict_full(features)
                
                # Guardar en session state para usar en el optimizador
                st.session_state['last_prediction'] = {
                    'features': features,
                    'results': prediction_results,
                    'expected_views': expected_views
                }
                
                # Mostrar resultados
                st.markdown("---")
                st.markdown("## 🎉 Resultados de la Predicción")
                
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    engagement_rate = prediction_results['engagement_rate']
                    st.metric(
                        "Engagement Rate",
                        f"{engagement_rate:.2f}%",
                        delta=None
                    )
                
                with col2:
                    category = prediction_results['category']
                    icon, text, color = format_engagement_category(category)
                    st.markdown(f"### {icon}")
                    st.markdown(f"**{category}**")
                
                with col3:
                    confidence = prediction_results['confidence']
                    max_prob = prediction_results['max_probability']
                    st.metric(
                        "Confianza",
                        confidence,
                        delta=f"{max_prob*100:.1f}%"
                    )
                
                with col4:
                    # Calcular métricas esperadas
                    expected_metrics = calculate_expected_metrics(engagement_rate, expected_views)
                    st.metric(
                        "Likes Esperados",
                        f"{expected_metrics['expected_likes']:,}"
                    )
                
                # Gráfico de probabilidades por categoría
                st.markdown("### 📊 Probabilidad por Categoría")
                
                prob_df = pd.DataFrame([
                    {'Categoría': cat, 'Probabilidad': prob*100}
                    for cat, prob in prediction_results['category_probabilities'].items()
                ]).sort_values('Probabilidad', ascending=False)
                
                fig_prob = px.bar(
                    prob_df,
                    x='Categoría',
                    y='Probabilidad',
                    title="Distribución de Probabilidades de Engagement",
                    labels={'Probabilidad': 'Probabilidad (%)'},
                    color='Probabilidad',
                    color_continuous_scale='RdYlGn'
                )
                
                fig_prob.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_prob, use_container_width=True)
                
                # Detalles de métricas esperadas
                st.markdown("### 📈 Métricas Esperadas")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Vistas", f"{expected_views:,}")
                
                with metric_col2:
                    st.metric("Likes", f"{expected_metrics['expected_likes']:,}")
                
                with metric_col3:
                    st.metric("Comentarios", f"{expected_metrics['expected_comments']:,}")
                
                with metric_col4:
                    st.metric("Engagement Total", f"{expected_metrics['expected_engagement_total']:,}")
                
                # Características del video analizadas
                st.markdown("### 🔍 Análisis de Características")
                
                analysis_col1, analysis_col2 = st.columns(2)
                
                with analysis_col1:
                    st.markdown("#### 📝 Título")
                    st.write(f"- Longitud: {features['title_length']} caracteres")
                    st.write(f"- Palabras: {features['title_word_count']}")
                    st.write(f"- Sentiment: {features['sentiment_compound']:.3f}")
                    st.write(f"- Tiene emoji: {'Sí' if features['title_has_emoji'] else 'No'}")
                    st.write(f"- Tiene pregunta: {'Sí' if features['title_has_question'] else 'No'}")
                    
                    st.markdown("#### ⏰ Timing")
                    st.write(f"- Hora de publicación: {publish_hour}:00")
                    st.write(f"- Día de semana: {features['publish_day_of_week']}")
                    st.write(f"- Es fin de semana: {'Sí' if features['is_weekend'] else 'No'}")
                    st.write(f"- Es hora pico: {'Sí' if features['is_peak_hour'] else 'No'}")
                
                with analysis_col2:
                    st.markdown("#### 🎬 Contenido")
                    st.write(f"- Duración: {duration_minutes:.1f} minutos")
                    st.write(f"- Categoría: {'Corto' if features['duration_category_short'] else 'Medio' if features['duration_category_medium'] else 'Largo'}")
                    st.write(f"- Tags: {features['tag_count']}")
                    st.write(f"- Descripción: {features['description_word_count']} palabras")
                    
                    st.markdown("#### 📢 Canal")
                    st.write(f"- Suscriptores: {subscriber_count:,}")
                    st.write(f"- Log(Suscriptores): {features['log_subscribers']:.2f}")
                
                # Exportar resultados
                st.markdown("---")
                st.markdown("### 💾 Exportar Resultados")
                
                export_data = {
                    'video_info': {
                        'titulo': title,
                        'suscriptores': subscriber_count,
                        'duracion_minutos': duration_minutes,
                        'fecha_publicacion': publish_datetime.strftime('%Y-%m-%d %H:%M'),
                        'vistas_esperadas': expected_views
                    },
                    'prediccion': {
                        'engagement_rate': f"{engagement_rate:.2f}%",
                        'categoria': category,
                        'confianza': confidence,
                        'likes_esperados': expected_metrics['expected_likes'],
                        'comentarios_esperados': expected_metrics['expected_comments']
                    },
                    'probabilidades': {
                        cat: f"{prob*100:.2f}%" 
                        for cat, prob in prediction_results['category_probabilities'].items()
                    }
                }
                
                import json
                export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
                
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    st.download_button(
                        label="📥 Descargar Predicción (JSON)",
                        data=export_json,
                        file_name=f"prediccion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col_exp2:
                    st.info("💡 Ahora ve al **Optimizador** para obtener recomendaciones de mejora")

except Exception as e:
    st.error(f"Error al cargar el predictor: {str(e)}")
    st.info("""
    **Posibles soluciones:**
    1. Verifica que los modelos estén entrenados en `03_Modelo_XGBoost_LightGBM/`
    2. Ejecuta el notebook `youtube_xgboost_predictor.ipynb` para generar los modelos
    3. Asegúrate de que las rutas relativas sean correctas
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Predicciones basadas en XGBoost + LightGBM | Confianza variable según datos de entrada</p>
</div>
""", unsafe_allow_html=True)
