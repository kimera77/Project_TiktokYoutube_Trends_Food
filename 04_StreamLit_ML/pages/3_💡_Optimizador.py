"""
Página de Optimizador - Recomendaciones para mejorar engagement
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from optimizer import VideoOptimizer
from utils import format_engagement_category

st.set_page_config(page_title="Optimizador", page_icon="💡", layout="wide")

# Estilos CSS para aumentar el tamaño del sidebar
st.markdown("""
<style>
    /* Aumentar tamaño de textos en sidebar */
    [data-testid="stSidebar"] * {
        font-size: 21px !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown {
        font-size: 21px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("💡 Optimizador de Videos")
st.markdown("### Recibe recomendaciones personalizadas para mejorar tu engagement")

# Inicializar optimizador
optimizer = VideoOptimizer()

# Verificar si hay una predicción previa
if 'last_prediction' in st.session_state:
    prediction_data = st.session_state['last_prediction']
    features = prediction_data['features']
    results = prediction_data['results']
    
    # Resumen de la predicción
    st.markdown("## 📊 Resumen de tu Video")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Título:** {features.get('title', 'N/A')[:50]}...")
        st.markdown(f"**Duración:** {features.get('duration_minutes', 0):.1f} minutos")
        st.markdown(f"**Suscriptores:** {features.get('subscriber_count', 0):,}")
    
    with col2:
        engagement_rate = results['engagement_rate']
        category = results['category']
        st.metric("Engagement Predicho", f"{engagement_rate:.2f}%")
        icon, text, color = format_engagement_category(category)
        st.markdown(f"### {icon} {category}")
    
    with col3:
        confidence = results['confidence']
        max_prob = results['max_probability']
        st.metric("Confianza", confidence, delta=f"{max_prob*100:.1f}%")
    
    st.markdown("---")
    
    # Generar recomendaciones
    with st.spinner("🔍 Analizando tu video..."):
        recommendations = optimizer.generate_recommendations(features, results)
    
    # Mostrar recomendaciones organizadas
    st.markdown("## 🎯 Recomendaciones de Optimización")
    
    # Críticas (si las hay)
    if recommendations['critical']:
        st.markdown("### 🚨 Problemas Críticos")
        st.error("Estos problemas deben corregirse antes de publicar:")
        
        for rec in recommendations['critical']:
            with st.expander(f"{rec['category']}: {rec['message']}", expanded=True):
                st.write(f"**Sugerencia:** {rec['suggestion']}")
    
    # Advertencias
    if recommendations['warnings']:
        st.markdown("### ⚠️ Advertencias")
        st.warning("Aspectos que pueden mejorarse para mejor rendimiento:")
        
        for rec in recommendations['warnings']:
            with st.expander(f"{rec['category']}: {rec['message']}"):
                st.write(f"**Sugerencia:** {rec['suggestion']}")
    
    # Información
    if recommendations['info']:
        st.markdown("### 💡 Sugerencias Adicionales")
        
        for rec in recommendations['info']:
            with st.expander(f"{rec['category']}: {rec['message']}"):
                st.write(f"**Sugerencia:** {rec['suggestion']}")
    
    # Éxitos
    if recommendations['success']:
        st.markdown("### ✅ Aspectos Positivos")
        st.success("Estos elementos están optimizados:")
        
        for rec in recommendations['success']:
            st.write(f"- {rec['message']}")
    
    # Puntuación general
    st.markdown("---")
    st.markdown("## 📈 Puntuación de Optimización")
    
    total_recommendations = sum(len(recs) for recs in recommendations.values())
    positive_count = len(recommendations['success'])
    score = (positive_count / total_recommendations * 100) if total_recommendations > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Puntuación General", f"{score:.0f}/100")
    
    with col2:
        st.metric("Aspectos Positivos", positive_count)
    
    with col3:
        issues_count = len(recommendations['critical']) + len(recommendations['warnings'])
        st.metric("Mejoras Necesarias", issues_count)
    
    # Barra de progreso
    progress_color = "green" if score >= 70 else "orange" if score >= 50 else "red"
    st.progress(score / 100)
    
    # Resumen de acción
    st.markdown("---")
    st.markdown("## 🎬 Plan de Acción")
    
    if score >= 80:
        st.success("""
        🎉 **¡Excelente!** Tu video está bien optimizado. 
        - Revisa las sugerencias adicionales para pulir detalles
        - Considera hacer pruebas A/B con diferentes miniaturas
        - Publica en el horario recomendado
        """)
    elif score >= 60:
        st.warning("""
        📊 **Buen trabajo**, pero hay margen de mejora:
        - Prioriza las advertencias marcadas
        - Optimiza el título según las recomendaciones
        - Revisa el timing de publicación
        """)
    else:
        st.error("""
        ⚠️ **Requiere optimización**:
        1. Corrige los problemas críticos primero
        2. Trabaja en las advertencias una por una
        3. Vuelve a ejecutar el predictor después de los cambios
        """)
    
    # Exportar recomendaciones
    st.markdown("---")
    st.markdown("### 💾 Exportar Recomendaciones")
    
    # Preparar datos para exportar
    export_text = f"""
REPORTE DE OPTIMIZACIÓN - YouTube Video
Generado: {st.session_state.get('timestamp', 'N/A')}

═══════════════════════════════════════════════════════
INFORMACIÓN DEL VIDEO
═══════════════════════════════════════════════════════
Título: {features.get('title', 'N/A')}
Duración: {features.get('duration_minutes', 0):.1f} minutos
Suscriptores: {features.get('subscriber_count', 0):,}

PREDICCIÓN
═══════════════════════════════════════════════════════
Engagement Rate: {engagement_rate:.2f}%
Categoría: {category}
Confianza: {confidence} ({max_prob*100:.1f}%)
Puntuación de Optimización: {score:.0f}/100

═══════════════════════════════════════════════════════
RECOMENDACIONES
═══════════════════════════════════════════════════════

"""
    
    if recommendations['critical']:
        export_text += "\n🚨 PROBLEMAS CRÍTICOS:\n" + "─" * 50 + "\n"
        for rec in recommendations['critical']:
            export_text += f"\n[{rec['category']}]\n{rec['message']}\n→ {rec['suggestion']}\n"
    
    if recommendations['warnings']:
        export_text += "\n\n⚠️ ADVERTENCIAS:\n" + "─" * 50 + "\n"
        for rec in recommendations['warnings']:
            export_text += f"\n[{rec['category']}]\n{rec['message']}\n→ {rec['suggestion']}\n"
    
    if recommendations['info']:
        export_text += "\n\n💡 SUGERENCIAS:\n" + "─" * 50 + "\n"
        for rec in recommendations['info']:
            export_text += f"\n[{rec['category']}]\n{rec['message']}\n→ {rec['suggestion']}\n"
    
    if recommendations['success']:
        export_text += "\n\n✅ ASPECTOS POSITIVOS:\n" + "─" * 50 + "\n"
        for rec in recommendations['success']:
            export_text += f"• {rec['message']}\n"
    
    export_text += f"""

═══════════════════════════════════════════════════════
PLAN DE ACCIÓN RECOMENDADO
═══════════════════════════════════════════════════════
1. Corregir problemas críticos: {len(recommendations['critical'])}
2. Revisar advertencias: {len(recommendations['warnings'])}
3. Aplicar sugerencias: {len(recommendations['info'])}
4. Volver a predecir después de cambios

═══════════════════════════════════════════════════════
Generado por YouTube ML Predictor | Proyecto Food Trends
═══════════════════════════════════════════════════════
"""
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.download_button(
            label="📥 Descargar Reporte Completo",
            data=export_text,
            file_name=f"reporte_optimizacion_{features.get('title', 'video')[:30]}.txt",
            mime="text/plain"
        )
    
    with col_exp2:
        st.info("💡 Guarda este reporte para referencia durante la edición de tu video")

else:
    # No hay predicción previa
    st.warning("⚠️ No hay ninguna predicción disponible")
    st.markdown("""
    Para recibir recomendaciones de optimización:
    
    1. Ve a la página **🎯 Predictor**
    2. Completa el formulario con la información de tu video
    3. Haz clic en **Predecir Engagement**
    4. Regresa aquí para ver las recomendaciones
    """)
    
    st.markdown("---")
    
    # Mostrar ejemplo de recomendaciones
    st.markdown("## 📚 Ejemplo de Recomendaciones")
    st.info("""
    Una vez que hagas una predicción, verás recomendaciones como:
    
    ✅ **Aspectos Positivos**
    - Longitud del título óptima (45 caracteres)
    - Publicación en hora pico (18:00)
    
    ⚠️ **Advertencias**
    - Título muy corto (20 caracteres). Recomendado: 30-70 caracteres
    - Video muy corto (2:15). Considera 3-10 minutos para mejor engagement
    
    💡 **Sugerencias**
    - Agregar palabras clave efectivas: "receta", "fácil", "rápido"
    - Incluir 1-2 emojis relevantes en el título
    - Optimizar descripción con más detalles (actualmente 15 palabras, recomendado 50-200)
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Recomendaciones basadas en análisis de miles de videos de comida exitosos</p>
</div>
""", unsafe_allow_html=True)
