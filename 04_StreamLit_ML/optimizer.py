"""
Optimizador de videos basado en reglas
Genera recomendaciones para mejorar el engagement del video
"""

import numpy as np
from datetime import datetime, time


class VideoOptimizer:
    """
    Genera recomendaciones basadas en reglas para optimizar el engagement
    """
    
    def __init__(self):
        """
        Inicializa el optimizador con reglas predefinidas
        """
        # Rangos óptimos basados en el análisis de datos
        self.optimal_ranges = {
            'title_length': (30, 70),
            'title_word_count': (5, 12),
            'duration': (180, 600),  # 3-10 minutos
            'publish_hour_optimal': [8, 9, 10, 12, 13, 18, 19, 20],
            'tag_count': (5, 15),
            'description_word_count': (50, 200)
        }
        
        # Palabras clave efectivas para títulos de comida
        self.effective_keywords = [
            'receta', 'fácil', 'rápido', 'delicioso', 'casero',
            'tutorial', 'paso a paso', 'mejor', 'secreto', 'perfecto',
            'tips', 'trucos', 'profesional', 'saludable', 'económico'
        ]
    
    def analyze_title(self, title, title_features):
        """
        Analiza el título y genera recomendaciones
        
        Args:
            title (str): Título del video
            title_features (dict): Características extraídas del título
            
        Returns:
            list: Lista de recomendaciones
        """
        recommendations = []
        
        # Longitud del título
        if title_features['title_length'] < self.optimal_ranges['title_length'][0]:
            recommendations.append({
                'type': 'warning',
                'category': 'Título',
                'message': f"📝 Título muy corto ({title_features['title_length']} caracteres). Recomendado: {self.optimal_ranges['title_length'][0]}-{self.optimal_ranges['title_length'][1]} caracteres.",
                'suggestion': "Agrega más detalles descriptivos sobre lo que hace único a tu receta."
            })
        elif title_features['title_length'] > self.optimal_ranges['title_length'][1]:
            recommendations.append({
                'type': 'warning',
                'category': 'Título',
                'message': f"📝 Título muy largo ({title_features['title_length']} caracteres). Recomendado: {self.optimal_ranges['title_length'][0]}-{self.optimal_ranges['title_length'][1]} caracteres.",
                'suggestion': "Simplifica el título manteniendo solo lo esencial y más atractivo."
            })
        else:
            recommendations.append({
                'type': 'success',
                'category': 'Título',
                'message': f"✅ Longitud del título óptima ({title_features['title_length']} caracteres).",
                'suggestion': ""
            })
        
        # Palabras clave efectivas
        title_lower = title.lower()
        found_keywords = [kw for kw in self.effective_keywords if kw in title_lower]
        
        if len(found_keywords) == 0:
            recommendations.append({
                'type': 'info',
                'category': 'Título',
                'message': "💡 No se detectaron palabras clave efectivas en el título.",
                'suggestion': f"Considera incluir palabras como: {', '.join(self.effective_keywords[:5])}..."
            })
        else:
            recommendations.append({
                'type': 'success',
                'category': 'Título',
                'message': f"✅ Palabras clave encontradas: {', '.join(found_keywords)}",
                'suggestion': ""
            })
        
        # Elementos de engagement
        if title_features['title_has_emoji'] == 0:
            recommendations.append({
                'type': 'info',
                'category': 'Título',
                'message': "😊 Sin emojis en el título.",
                'suggestion': "Agregar 1-2 emojis relevantes puede aumentar el CTR (ej: 🍕🔥)."
            })
        
        if title_features['title_question_count'] == 0 and title_features['title_exclamation_count'] == 0:
            recommendations.append({
                'type': 'info',
                'category': 'Título',
                'message': "❓ El título no genera curiosidad ni emoción.",
                'suggestion': "Considera usar preguntas (¿Cómo hacer...?) o exclamaciones (¡El mejor...!)."
            })
        
        return recommendations
    
    def analyze_timing(self, temporal_features):
        """
        Analiza el timing de publicación y genera recomendaciones
        
        Args:
            temporal_features (dict): Características temporales
            
        Returns:
            list: Lista de recomendaciones
        """
        recommendations = []
        
        publish_hour = temporal_features.get('publish_hour', 18)  # Default 18:00 si no existe
        is_weekend = temporal_features.get('is_weekend', 0)
        is_prime_time = temporal_features.get('is_prime_time', 0)  # Usar is_prime_time en lugar de is_peak_hour
        
        # Hora de publicación
        if is_prime_time:
            recommendations.append({
                'type': 'success',
                'category': 'Timing',
                'message': f"✅ Publicación en hora pico ({publish_hour}:00).",
                'suggestion': ""
            })
        else:
            recommendations.append({
                'type': 'warning',
                'category': 'Timing',
                'message': f"⏰ Publicación en hora no óptima ({publish_hour}:00).",
                'suggestion': f"Considera publicar en horas pico: 18:00-22:00 (prime time)"
            })
        
        # Fin de semana
        if is_weekend:
            recommendations.append({
                'type': 'info',
                'category': 'Timing',
                'message': "📅 Publicación en fin de semana.",
                'suggestion': "Los fines de semana pueden tener menos alcance inicial pero mejor engagement prolongado."
            })
        else:
            recommendations.append({
                'type': 'success',
                'category': 'Timing',
                'message': "📅 Publicación entre semana (mejor para alcance viral rápido).",
                'suggestion': ""
            })
        
        return recommendations
    
    def analyze_content(self, content_features):
        """
        Analiza el contenido del video y genera recomendaciones
        
        Args:
            content_features (dict): Características del contenido
            
        Returns:
            list: Lista de recomendaciones
        """
        recommendations = []
        
        # Usar duration_sec si duration no existe
        duration = content_features.get('duration', content_features.get('duration_sec', 0))
        tag_count = content_features.get('tag_count', 0)
        has_desc = content_features.get('has_description', 0)
        
        # Duración del video
        if duration < self.optimal_ranges['duration'][0]:
            recommendations.append({
                'type': 'warning',
                'category': 'Contenido',
                'message': f"⏱️ Video muy corto ({duration//60}:{duration%60:02d}).",
                'suggestion': f"Videos de {self.optimal_ranges['duration'][0]//60}-{self.optimal_ranges['duration'][1]//60} minutos tienen mejor engagement."
            })
        elif duration > self.optimal_ranges['duration'][1]:
            recommendations.append({
                'type': 'warning',
                'category': 'Contenido',
                'message': f"⏱️ Video muy largo ({duration//60}:{duration%60:02d}).",
                'suggestion': "Videos largos requieren edición dinámica para mantener atención. Considera dividir en partes."
            })
        else:
            recommendations.append({
                'type': 'success',
                'category': 'Contenido',
                'message': f"✅ Duración óptima ({duration//60}:{duration%60:02d}).",
                'suggestion': ""
            })
        
        # Tags
        if tag_count < self.optimal_ranges['tag_count'][0]:
            recommendations.append({
                'type': 'warning',
                'category': 'Contenido',
                'message': f"🏷️ Pocos tags ({tag_count}).",
                'suggestion': f"Usa {self.optimal_ranges['tag_count'][0]}-{self.optimal_ranges['tag_count'][1]} tags relevantes para mejor descubrimiento."
            })
        elif tag_count > self.optimal_ranges['tag_count'][1]:
            recommendations.append({
                'type': 'info',
                'category': 'Contenido',
                'message': f"🏷️ Muchos tags ({tag_count}).",
                'suggestion': "Demasiados tags pueden diluir relevancia. Enfócate en los más importantes."
            })
        else:
            recommendations.append({
                'type': 'success',
                'category': 'Contenido',
                'message': f"✅ Número óptimo de tags ({tag_count}).",
                'suggestion': ""
            })
        
        # Descripción
        if not has_desc:
            recommendations.append({
                'type': 'error',
                'category': 'Contenido',
                'message': "❌ Sin descripción.",
                'suggestion': "Agrega una descripción detallada con ingredientes, pasos y palabras clave para SEO."
            })
        else:
            # Calcular description_word_count si no existe
            desc_words = content_features.get('description_word_count', 
                                             len(content_features.get('description', '').split()))
            if desc_words < self.optimal_ranges['description_word_count'][0]:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Contenido',
                    'message': f"📄 Descripción muy corta ({desc_words} palabras).",
                    'suggestion': "Expande la descripción con ingredientes completos, tips y enlaces."
                })
            else:
                recommendations.append({
                    'type': 'success',
                    'category': 'Contenido',
                    'message': f"✅ Descripción completa ({desc_words} palabras).",
                    'suggestion': ""
                })
        
        return recommendations
    
    def analyze_channel(self, channel_features):
        """
        Analiza las características del canal y genera recomendaciones
        
        Args:
            channel_features (dict): Características del canal
            
        Returns:
            list: Lista de recomendaciones
        """
        recommendations = []
        
        subscribers = channel_features.get('subscriber_count', 0)
        
        if subscribers < 1000:
            recommendations.append({
                'type': 'info',
                'category': 'Canal',
                'message': f"📢 Canal pequeño ({subscribers:,} suscriptores).",
                'suggestion': "Enfócate en nichos específicos y colaboraciones con canales similares."
            })
        elif subscribers < 10000:
            recommendations.append({
                'type': 'info',
                'category': 'Canal',
                'message': f"📈 Canal en crecimiento ({subscribers:,} suscriptores).",
                'suggestion': "Mantén consistencia en publicación (2-3 videos/semana) para acelerar crecimiento."
            })
        elif subscribers < 100000:
            recommendations.append({
                'type': 'success',
                'category': 'Canal',
                'message': f"🎯 Canal establecido ({subscribers:,} suscriptores).",
                'suggestion': "Optimiza miniatura y primeros 10 segundos para maximizar CTR."
            })
        else:
            recommendations.append({
                'type': 'success',
                'category': 'Canal',
                'message': f"⭐ Canal grande ({subscribers:,} suscriptores).",
                'suggestion': "Experimenta con formatos nuevos y analiza qué videos impulsan más suscriptores."
            })
        
        return recommendations
    
    def generate_recommendations(self, features_dict, prediction_results):
        """
        Genera todas las recomendaciones basadas en características y predicciones
        
        Args:
            features_dict (dict): Todas las características del video
            prediction_results (dict): Resultados de la predicción
            
        Returns:
            dict: Diccionario organizado con todas las recomendaciones
        """
        all_recommendations = []
        
        # Analizar título
        title_recs = self.analyze_title(
            features_dict.get('title', ''),
            features_dict
        )
        all_recommendations.extend(title_recs)
        
        # Analizar timing
        timing_recs = self.analyze_timing(features_dict)
        all_recommendations.extend(timing_recs)
        
        # Analizar contenido
        content_recs = self.analyze_content(features_dict)
        all_recommendations.extend(content_recs)
        
        # Analizar canal
        channel_recs = self.analyze_channel(features_dict)
        all_recommendations.extend(channel_recs)
        
        # Análisis de predicción
        engagement_rate = prediction_results['engagement_rate']
        category = prediction_results['category']
        
        if engagement_rate < 2.0:
            all_recommendations.append({
                'type': 'error',
                'category': 'Predicción',
                'message': f"⚠️ Engagement predicho muy bajo ({engagement_rate:.2f}%).",
                'suggestion': "Considera aplicar las recomendaciones antes de publicar para mejorar resultados."
            })
        elif engagement_rate < 5.0:
            all_recommendations.append({
                'type': 'warning',
                'category': 'Predicción',
                'message': f"📊 Engagement predicho medio ({engagement_rate:.2f}%).",
                'suggestion': "Optimiza título y timing para alcanzar engagement alto (>5%)."
            })
        else:
            all_recommendations.append({
                'type': 'success',
                'category': 'Predicción',
                'message': f"🎉 Engagement predicho excelente ({engagement_rate:.2f}%).",
                'suggestion': "Mantén estos elementos en futuros videos."
            })
        
        # Organizar por categoría y tipo
        organized = {
            'critical': [r for r in all_recommendations if r['type'] == 'error'],
            'warnings': [r for r in all_recommendations if r['type'] == 'warning'],
            'info': [r for r in all_recommendations if r['type'] == 'info'],
            'success': [r for r in all_recommendations if r['type'] == 'success']
        }
        
        return organized
