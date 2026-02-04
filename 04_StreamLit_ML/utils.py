"""
Utilidades para feature engineering y procesamiento de datos
Réplica de las funciones del notebook youtube_xgboost_predictor.ipynb
"""

import pandas as pd
import numpy as np
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Inicializar analizador de sentimiento
sentiment_analyzer = SentimentIntensityAnalyzer()


def extract_sentiment_features(title):
    """
    Extrae características de sentimiento del título usando VADER
    
    Args:
        title (str): Título del video
        
    Returns:
        dict: Diccionario con características de sentimiento
    """
    scores = sentiment_analyzer.polarity_scores(title)
    return {
        'title_sentiment_positive': scores['pos'],
        'title_sentiment_negative': scores['neg'],
        'title_sentiment_neutral': scores['neu'],
        'title_sentiment_compound': scores['compound']
    }


def extract_title_features(title):
    """
    Extrae características del título del video
    
    Args:
        title (str): Título del video
        
    Returns:
        dict: Diccionario con características del título
    """
    features = {}
    
    # Longitud del título
    features['title_length'] = len(title)
    
    # Número de palabras
    features['title_word_count'] = len(title.split())
    
    # Ratio de mayúsculas
    if len(title) > 0:
        uppercase_count = sum(1 for c in title if c.isupper())
        features['title_uppercase_ratio'] = uppercase_count / len(title)
    else:
        features['title_uppercase_ratio'] = 0
    
    # Emojis (detección simple)
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags
                               "]+", flags=re.UNICODE)
    features['title_has_emoji'] = int(bool(emoji_pattern.search(title)))
    
    # Exclamaciones
    features['title_exclamation_count'] = title.count('!')
    
    # Preguntas
    features['title_question_count'] = title.count('?')
    
    # Números en el título
    features['title_has_number'] = int(bool(re.search(r'\d', title)))
    
    # Hashtags
    features['title_hashtag_count'] = title.count('#')
    
    return features


def extract_temporal_features(publish_date):
    """
    Extrae características temporales de la fecha de publicación
    
    Args:
        publish_date (str or datetime): Fecha de publicación
        
    Returns:
        dict: Diccionario con características temporales
    """
    if isinstance(publish_date, str):
        pub_date = pd.to_datetime(publish_date)
    else:
        pub_date = publish_date
    
    features = {}
    # Usar weekday() para datetime, dayofweek para pandas
    day_of_week = pub_date.weekday() if hasattr(pub_date, 'weekday') else pub_date.dayofweek
    hour = pub_date.hour
    
    # Características básicas (NO incluir estas que no están en el modelo)
    # features['publish_hour'] y publish_day_of_week se usan solo para calcular otras features
    
    # Características temporales que SÍ están en el modelo
    features['is_weekend'] = int(day_of_week >= 5)
    features['is_prime_time'] = int(18 <= hour <= 22)  # 6PM-10PM
    features['is_morning'] = int(6 <= hour <= 12)      # 6AM-12PM
    features['is_afternoon'] = int(12 < hour <= 18)    # 12PM-6PM
    
    return features


def categorize_channel_size(subscribers):
    """
    Categoriza el tamaño del canal según número de suscriptores
    """
    if subscribers < 1000:
        return 0  # Micro
    elif subscribers < 10000:
        return 1  # Small
    elif subscribers < 100000:
        return 2  # Medium
    elif subscribers < 1000000:
        return 3  # Large
    else:
        return 4  # Mega


def extract_channel_features(subscriber_count):
    """
    Extrae características del canal
    
    Args:
        subscriber_count (int): Número de suscriptores
        
    Returns:
        dict: Diccionario con características del canal
    """
    features = {}
    features['subscriber_count'] = subscriber_count
    features['log_subscribers'] = np.log1p(subscriber_count)
    features['channel_size_category'] = categorize_channel_size(subscriber_count)
    
    return features


def extract_content_features(duration, tags, description):
    """
    Extrae características del contenido del video
    
    Args:
        duration (int): Duración del video en segundos
        tags (str or list): Tags del video (puede ser string separado por comas o lista)
        description (str): Descripción del video
        
    Returns:
        dict: Diccionario con características del contenido
    """
    features = {}
    
    # Duración (en segundos)
    features['duration_sec'] = duration
    features['duration'] = duration
    features['log_duration'] = np.log1p(duration)
    features['duration_minutes'] = duration / 60
    
    # Categorías de duración (binarias)
    features['is_short'] = int(duration <= 60)  # <= 1 minuto
    features['is_medium'] = int(60 < duration <= 600)  # 1-10 min
    features['is_long'] = int(duration > 600)  # > 10 min
    
    # Categoría de duración (one-hot encoding)
    if duration < 60:
        features['duration_category_short'] = 1
        features['duration_category_medium'] = 0
        features['duration_category_long'] = 0
    elif duration < 600:
        features['duration_category_short'] = 0
        features['duration_category_medium'] = 1
        features['duration_category_long'] = 0
    else:
        features['duration_category_short'] = 0
        features['duration_category_medium'] = 0
        features['duration_category_long'] = 1
    
    # Tags
    if isinstance(tags, str):
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
    else:
        tags_list = tags if tags else []
    
    features['tag_count'] = len(tags_list)
    features['log_tag_count'] = np.log1p(len(tags_list))
    features['has_tags'] = int(len(tags_list) > 0)
    
    # Descripción
    desc_text = description if description else ""
    features['description_length'] = len(desc_text)
    features['description_word_count'] = len(desc_text.split())
    features['has_description'] = int(len(desc_text) > 0)
    
    # Captions (asumir que videos con descripción larga tienen captions)
    features['has_captions'] = int(len(desc_text) > 100)
    
    # Features adicionales de video (valores por defecto)
    features['is_hd'] = 1  # Asumir HD por defecto
    
    return features


def create_features_from_input(
    title,
    subscriber_count,
    duration,
    publish_date=None,
    tags="",
    description=""
):
    """
    Crea todas las características a partir de los inputs del usuario
    
    Args:
        title (str): Título del video
        subscriber_count (int): Número de suscriptores del canal
        duration (int): Duración del video en segundos
        publish_date (str or datetime, optional): Fecha de publicación
        tags (str, optional): Tags separados por comas
        description (str, optional): Descripción del video
        
    Returns:
        dict: Diccionario con todas las características
    """
    features = {}
    
    # Características de sentimiento
    features.update(extract_sentiment_features(title))
    
    # Características del título
    features.update(extract_title_features(title))
    
    # Características temporales
    if publish_date:
        features.update(extract_temporal_features(publish_date))
    else:
        # Usar fecha actual si no se proporciona
        features.update(extract_temporal_features(datetime.now()))
    
    # Características del canal
    features.update(extract_channel_features(subscriber_count))
    
    # Características del contenido
    features.update(extract_content_features(duration, tags, description))
    
    # Features adicionales con valores por defecto
    features['made_for_kids'] = 0  # Por defecto, no es para niños
    features['category_encoded'] = 0  # 0 para "Food" (valor por defecto)
    features['language_encoded'] = 0  # 0 para idioma por defecto
    
    # Guardar título original para referencia
    features['title'] = title
    
    # Ordenar features en el orden exacto que espera el modelo
    feature_order = [
        'tag_count', 'duration_sec', 'subscriber_count', 'made_for_kids',
        'title_sentiment_compound', 'title_sentiment_positive', 'title_sentiment_negative', 'title_sentiment_neutral',
        'title_length', 'title_word_count', 'title_uppercase_ratio', 'title_has_emoji',
        'title_exclamation_count', 'title_question_count', 'title_has_number', 'title_hashtag_count',
        'is_weekend', 'is_prime_time', 'is_morning', 'is_afternoon',
        'channel_size_category', 'log_subscribers', 'duration_minutes',
        'is_short', 'is_medium', 'is_long',
        'description_length', 'has_description', 'has_tags', 'log_tag_count',
        'is_hd', 'has_captions', 'category_encoded', 'language_encoded'
    ]
    
    # Crear diccionario ordenado con todas las features necesarias
    ordered_features = {}
    for feat in feature_order:
        ordered_features[feat] = features.get(feat, 0)  # 0 por defecto si falta
    
    # Mantener el título para referencia (no se usa en el modelo)
    ordered_features['title'] = title
    
    # Agregar campos adicionales necesarios para el optimizador
    ordered_features['duration'] = features.get('duration', duration)
    ordered_features['description_word_count'] = features.get('description_word_count', 0)
    ordered_features['title_has_emoji'] = features.get('title_has_emoji', 0)
    ordered_features['title_question_count'] = features.get('title_question_count', 0)
    ordered_features['title_exclamation_count'] = features.get('title_exclamation_count', 0)
    
    return ordered_features


def format_engagement_category(category):
    """
    Formatea la categoría de engagement para mostrar al usuario
    
    Args:
        category (str): Categoría predicha
        
    Returns:
        tuple: (icono, texto, color)
    """
    category_info = {
        'Bajo': ('📉', 'Engagement Bajo (<2%)', '#ff4444'),
        'Medio': ('📊', 'Engagement Medio (2-5%)', '#ffaa00'),
        'Alto': ('📈', 'Engagement Alto (5-10%)', '#44ff44'),
        'Viral': ('🚀', 'Engagement Viral (>10%)', '#ff44ff')
    }
    
    return category_info.get(category, ('❓', 'Desconocido', '#888888'))


def calculate_expected_metrics(engagement_rate, expected_views):
    """
    Calcula métricas esperadas basadas en el engagement rate predicho y vistas esperadas
    
    Args:
        engagement_rate (float): Tasa de engagement predicha
        expected_views (int): Número esperado de vistas
        
    Returns:
        dict: Diccionario con métricas calculadas
    """
    # Fórmula inversa: engagement_rate = (likes + 50*comments) / views * 100
    # Asumiendo proporción típica: likes ~= 10 * comments
    
    total_engagement = (engagement_rate * expected_views) / 100
    
    # Distribución aproximada: 90% likes, 10% comments (ponderado por 50)
    # likes + 50*comments = total_engagement
    # Si likes = 10*comments: 10*comments + 50*comments = 60*comments
    estimated_comments = total_engagement / 60
    estimated_likes = total_engagement - (50 * estimated_comments)
    
    return {
        'expected_likes': int(max(0, estimated_likes)),
        'expected_comments': int(max(0, estimated_comments)),
        'expected_engagement_total': int(total_engagement)
    }
