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
        'sentiment_pos': scores['pos'],
        'sentiment_neg': scores['neg'],
        'sentiment_neu': scores['neu'],
        'sentiment_compound': scores['compound']
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
    
    # Palabras en mayúsculas
    features['title_uppercase_words'] = sum(1 for word in title.split() if word.isupper())
    
    # Caracteres especiales
    features['title_special_chars'] = len(re.findall(r'[!?@#$%^&*()_+={}\[\]:;"\'<>,./-]', title))
    
    # Números en el título
    features['title_has_numbers'] = int(bool(re.search(r'\d', title)))
    
    # Emojis (detección simple)
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags
                               "]+", flags=re.UNICODE)
    features['title_has_emoji'] = int(bool(emoji_pattern.search(title)))
    
    # Preguntas
    features['title_has_question'] = int('?' in title)
    
    # Exclamaciones
    features['title_exclamation_count'] = title.count('!')
    
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
    features['publish_hour'] = pub_date.hour
    features['publish_day_of_week'] = pub_date.dayofweek
    features['publish_day'] = pub_date.day
    features['publish_month'] = pub_date.month
    features['publish_year'] = pub_date.year
    features['is_weekend'] = int(pub_date.dayofweek >= 5)
    
    # Horas pico (8-10am, 12-2pm, 6-10pm)
    is_peak = (8 <= pub_date.hour <= 10) or (12 <= pub_date.hour <= 14) or (18 <= pub_date.hour <= 22)
    features['is_peak_hour'] = int(is_peak)
    
    # Días desde publicación (respecto a fecha actual simulada)
    current_date = datetime.now()
    days_since = (current_date - pub_date).days
    features['days_since_publish'] = days_since
    features['log_days_since_publish'] = np.log1p(days_since)
    
    return features


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
    
    # Duración
    features['duration'] = duration
    features['log_duration'] = np.log1p(duration)
    features['duration_minutes'] = duration / 60
    
    # Categoría de duración
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
    
    # Descripción
    desc_text = description if description else ""
    features['description_length'] = len(desc_text)
    features['description_word_count'] = len(desc_text.split())
    features['has_description'] = int(len(desc_text) > 0)
    
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
    
    return features


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
