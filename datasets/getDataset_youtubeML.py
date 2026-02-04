import os
import pandas as pd
import isodate
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory

# Consistencia en detección de idioma
DetectorFactory.seed = 0

# --- CONFIGURACIÓN ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Obtener directorio del script para guardar siempre en datasets/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(SCRIPT_DIR, 'dataset_ML_food.csv')

# ==========================================
# KEYWORDS DE COMIDA (FILTRO MEJORADO)
# ==========================================

YOUTUBE_CATEGORIES = {
    '1': 'Film & Animation', '2': 'Autos & Vehicles', '10': 'Music',
    '15': 'Pets & Animals', '17': 'Sports', '19': 'Travel & Events',
    '20': 'Gaming', '22': 'People & Blogs', '23': 'Comedy',
    '24': 'Entertainment', '25': 'News & Politics', '26': 'Howto & Style',
    '27': 'Education', '28': 'Science & Technology', '29': 'Nonprofits & Activism'
}

FOOD_KEYWORDS_TITLE = [
    # Comida general
    'food', 'foods', 'foodie', 'eat', 'eating', 'eats', 'taste', 'tasting', 'yummy', 'delicious',
    
    # Cooking
    'cook', 'cooking', 'cooked', 'recipe', 'recipes', 'chef', 'kitchen', 'bake', 'baking',
    'fry', 'fried', 'grill', 'grilled', 'bbq', 'roast', 'roasted', 'boil', 'steam',
    
    # Tipos de comida
    'pizza', 'burger', 'burgers', 'pasta', 'noodles', 'ramen', 'sushi', 'tacos', 'sandwich',
    'salad', 'soup', 'steak', 'chicken', 'beef', 'pork', 'fish', 'seafood', 'shrimp',
    'bread', 'cake', 'dessert', 'desserts', 'cookie', 'cookies', 'pie', 'pastry',
]

FOOD_TOPIC_CATEGORIES = ["Food", "Cooking", "Cuisine", "Beverage", "Drink", "Recipe"]


def get_existing_ids():
    if os.path.exists(FILE_NAME):
        try:
            df_existing = pd.read_csv(FILE_NAME, usecols=['video_id'])
            return set(df_existing['video_id'].astype(str).tolist())
        except: 
            return set()
    return set()


def clean_topic_url(url_list):
    """Limpia las URLs de Wikipedia a nombres de categorías simples."""
    if not url_list:
        return ""
    clean_list = []
    for url in url_list:
        name = url.split('/')[-1].replace('_', ' ')
        # Elimina cualquier texto entre paréntesis
        name = re.sub(r'\s*\([^)]*\)', '', name)
        name = name.strip()
        clean_list.append(name)
    return ",".join(clean_list)

# --- CAMBIO 2: Función para extraer música de la descripción ---
def extract_music_info(description):
    if not description:
        return "None detected"
    patterns = [r"Song:\s*(.*)", r"Artist:\s*(.*)", r"Music in this video\s*Learn more\s*Song\s*(.*)"]
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).split('\n')[0].strip()
    return "None detected"

# --- CAMBIO 3: Detección de idioma mejorada con metadatos y más texto ---
def is_wanted_language(title, description, audio_lang, text_lang):
    # Primero check de metadatos oficiales de YouTube
    if audio_lang and not audio_lang.startswith('en'):
        return False
    if text_lang and not text_lang.startswith('en'):
        return False
    
    # Luego detección por texto (combinamos título y descripción)
    texto_para_detectar = f"{title} {description[:100]}"
    if len(texto_para_detectar.strip()) < 8:
        return False
    try:
        lang = detect(texto_para_detectar)
        return lang in ['en']
    except: 
        return False


def detectar_comida_en_texto(texto, keywords_list):
    """Detecta palabras clave de comida en el texto"""
    if not texto:
        return False
    
    texto_lower = texto.lower()
    
    for keyword in keywords_list:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, texto_lower):
            return True
    
    return False


def es_comida_por_titulo(title, tags, topics):
    """
    FILTRO OPTIMIZADO: Verifica si es contenido de comida
    Busca en título, tags Y topics (cualquiera de los 3 sirve)
    """
    # 1. Búsqueda en TÍTULO (la más importante)
    if detectar_comida_en_texto(title, FOOD_KEYWORDS_TITLE):
        return True
    
    # 2. Búsqueda en TAGS
    if tags:
        tags_text = " ".join(tags) if isinstance(tags, list) else str(tags)
        if detectar_comida_en_texto(tags_text, FOOD_KEYWORDS_TITLE):
            return True
    
    # 3. Topic Categories de YouTube (como backup)
    topics_text = str(topics)
    if any(t in topics_text for t in FOOD_TOPIC_CATEGORIES):
        return True
    
    return False


def get_channel_subs(channel_ids):
    """Obtiene subscriber count de los canales (como en tu código original)"""
    if not channel_ids: 
        return {}
    
    try:
        res = youtube.channels().list(
            part="statistics", 
            id=",".join(channel_ids)
        ).execute()
        return {item['id']: int(item['statistics'].get('subscriberCount', 0)) 
                for item in res.get('items', [])}
    except HttpError as e:
        if 'quotaExceeded' in str(e):
            raise
        return {}


def get_shorts_massive():
    # Ventana de 3 días para estabilidad de datos (COMO EN TU CÓDIGO ORIGINAL)
    target_day = datetime.now(timezone.utc) - timedelta(days=3)
    # Cambia estas líneas:
    start_date = target_day.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date = target_day.replace(hour=23, minute=59, second=59, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    print(f"📅 Buscando videos del: {target_day.strftime('%Y-%m-%d (%A)')}")
    
    existing_ids = get_existing_ids()
    
    # Queries diversificadas (COMO EN TU CÓDIGO ORIGINAL, pero descomentadas)
    queries = [
        # General & Lifestyle
        "food", "street food", "food review", "tasting food", "best food", 
        "viral food", "food asmr", "mukbang",
        
        # Cooking & Skills
        "cooking hacks", "kitchen gadgets", "recipe",
        "chef life", "home cooking", "baking", "pastry", "grilling", "bbq", "cooking techniques",
        
        # Specifics & Trends
        "healthy food", "meal prep", "budget meals", "fast food", 
        "junk food", "pizza", "burger", "coffee", "desserts", "food challenge"
    ]


    total_new_videos = 0
    quota_exceeded = False

    for q in queries:
        if quota_exceeded:
            break
            
        print(f"🔍 Buscando: {q}...")
        next_page_token = None
        
        # 10 páginas por query (COMO EN TU CÓDIGO ORIGINAL) 
        for i in range(10): 
            if quota_exceeded:
                break
                
            try:
                search_request = youtube.search().list(
                    q=q, 
                    part="id", 
                    type="video", 
                    videoDuration="short",
                    relevanceLanguage="en",
                    publishedAfter=start_date, 
                    publishedBefore=end_date,
                    maxResults=50, 
                    order="date",
                    pageToken=next_page_token
                )
                search_response = search_request.execute()
                
            except HttpError as e:
                if 'quotaExceeded' in str(e):
                    print(f"\n⚠️ CUOTA DE API AGOTADA")
                    quota_exceeded = True
                    break
                else:
                    print(f"❌ Error en búsqueda: {e}")
                    continue
            
            found_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            new_ids = [vid for vid in found_ids if vid not in existing_ids]

            if not new_ids:
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token: 
                    break
                continue

            try:
                # Llamada de detalles (COMO EN TU CÓDIGO ORIGINAL)
                v_res = youtube.videos().list(
                    part="snippet,statistics,contentDetails,topicDetails,status",
                    id=",".join(new_ids)
                ).execute()

            except HttpError as e:
                if 'quotaExceeded' in str(e):
                    print(f"\n⚠️ CUOTA DE API AGOTADA")
                    quota_exceeded = True
                    break
                else:
                    print(f"❌ Error obteniendo detalles: {e}")
                    continue

            channel_ids = list(set([v['snippet']['channelId'] for v in v_res.get('items', [])]))
            
            try:
                subs_map = get_channel_subs(channel_ids)
            except HttpError as e:
                if 'quotaExceeded' in str(e):
                    print(f"\n⚠️ CUOTA DE API AGOTADA")
                    quota_exceeded = True
                    break
                else:
                    subs_map = {}

            video_batch = []
            for video in v_res.get('items', []):
                snippet = video['snippet']
                title = snippet['title']
                description = snippet.get('description', '') # <--- Necesario para nuevos filtros
                cat_id = snippet.get('categoryId')
                
                # --- ACTUALIZACIÓN FILTRO IDIOMA ---
                audio_lang = snippet.get('defaultAudioLanguage')
                text_lang = snippet.get('defaultLanguage')
                if not is_wanted_language(title, description, audio_lang, text_lang): 
                    continue
                
                content = video['contentDetails']
                
                # Control if duration no exist (COMO EN TU CÓDIGO ORIGINAL)
                raw_duration = content.get('duration')
                if not raw_duration:
                    continue
                    
                duration_sec = isodate.parse_duration(raw_duration).total_seconds()
                
                # Extraer tags correctamente (CORREGIDO)
                tags = snippet.get('tags', [])
                
                raw_topics = video.get('topicDetails', {}).get('topicCategories', [])
                
                # FILTRO MEJORADO: Duración <= 60 Y (título O tags O topics de comida)
                if duration_sec <= 60 and es_comida_por_titulo(title, tags, raw_topics):
                    stats = video['statistics']
                    
                    views = int(stats.get('viewCount', 0))
                    likes = int(stats.get('likeCount', 0))
                    comments = int(stats.get('commentCount', 0))
                    
                    # Calcular age_hours para views_per_hour DEL VIDEO (no del canal)
                    published = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                    age_hours = (datetime.now(timezone.utc) - published).total_seconds() / 3600

                    video_batch.append({
                        'video_id': video['id'],
                        'title': title,
                        'description': description,
                        'published_at': snippet.get('publishedAt'),
                        'channel_id': snippet.get('channelId'),
                        'channel_title': snippet.get('channelTitle'),
                        'category_id': cat_id,
                        'category_name': YOUTUBE_CATEGORIES.get(cat_id, "Unknown"), # <--- ACTUALIZACIÓN: Literal de categoría
                        'tags': "|".join(tags),
                        'tag_count': len(tags),
                        'duration_sec': duration_sec,
                        'definition': content.get('definition'),
                        'caption': content.get('caption'),
                        'licensed_content': content.get('licensedContent'), 
                        'view_count': views,
                        'like_count': likes,
                        'comment_count': comments,
                        'default_audio_lang': audio_lang,
                        'music_info': extract_music_info(description), # <--- ACTUALIZACIÓN: Nueva columna música
                        'url': f"https://www.youtube.com/shorts/{video['id']}",
                        
                        # NUEVAS COLUMNAS AÑADIDAS (con tus correcciones):
                        'subscriber_count': subs_map.get(snippet.get('channelId'), 0),
                        'made_for_kids': 1 if video.get('status', {}).get('madeForKids') else 0,
                        'views_per_hour': round(views / age_hours, 2) if age_hours > 0 else 0,  # DEL VIDEO
                        'publish_day_of_week': published.strftime('%A'),  # Del día que se publicó (hace 3 días)
                    })                    
                    
                    existing_ids.add(video['id'])

            if video_batch:
                df = pd.DataFrame(video_batch)
                df.to_csv(FILE_NAME, mode='a', index=False, 
                         header=not os.path.exists(FILE_NAME), encoding='utf-8-sig')
                total_new_videos += len(video_batch)

            next_page_token = search_response.get('nextPageToken')
            if not next_page_token: 
                break
            
    print(f"🏁 Finalizado. Se han añadido {total_new_videos} videos nuevos al histórico.")
    
    if quota_exceeded:
        print(f"⏰ La cuota se agotó. Vuelve a ejecutar mañana para continuar.")

if __name__ == "__main__":
    get_shorts_massive()