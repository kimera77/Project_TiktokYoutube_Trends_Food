import os
import pandas as pd
import isodate
import re
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
#pip install langdetect pandas google-api-python-client isodate python-dotenv

# Consistencia en detección de idioma
DetectorFactory.seed = 0

# --- CONFIGURACIÓN ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)
FILE_NAME = 'dataSet_ML_food.csv'

def get_existing_ids():
    if os.path.exists(FILE_NAME):
        try:
            df_existing = pd.read_csv(FILE_NAME, usecols=['video_id'])
            return set(df_existing['video_id'].astype(str).tolist())
        except: return set()
    return set()

def clean_topic_url(url_list):
    """Limpia las URLs de Wikipedia a nombres de categorías simples (Tu versión optimizada)."""
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

def is_wanted_language(text):
    try:
        lang = detect(text)
        return lang in ['en']
    except: return False

def get_channel_subs(channel_ids):
    if not channel_ids: return {}
    res = youtube.channels().list(part="statistics", id=",".join(channel_ids)).execute()
    return {item['id']: int(item['statistics'].get('subscriberCount', 0)) for item in res.get('items', [])}

def get_shorts_massive():
    # Ventana de 3 días para estabilidad de datos
    target_day = datetime.now(timezone.utc) - timedelta(days=3)
    start_date = target_day.replace(hour=0, minute=0, second=0).isoformat()
    end_date = target_day.replace(hour=23, minute=59, second=59).isoformat()
    
    existing_ids = get_existing_ids()
    
    # Queries diversificadas (sin recetas/recipes) para maximizar volumen

    # queries = [
    # # General & Lifestyle
    # "foodie", "street food", "food review", "tasting food", "best food", 
    # "viral food", "satisfying food", "food asmr", "mukbang",
    
    # # Cooking & Skills
    # "cooking hacks", "kitchen gadgets", "recipe", "easy recipes", 
    # "chef life", "home cooking", "baking", "pastry", "grilling", "bbq","cooking techniques","bbq"
    
    # # Specifics & Trends
    # "healthy food", "meal prep", "budget meals", "fast food", 
    # "junk food", "pizza", "burger", "coffee", "desserts", "food challenge",
    
    # # Short-form specific
    # "shorts food", "cooking shorts", "food trends 2026"]
    queries = ["food"]
    
    total_new_videos = 0

    for q in queries:
        print(f"🔍 Buscando: {q}...")
        next_page_token = None
        
        # Subimos a 10 páginas por query para aprovechar la cuota
        for i in range(10): 
            search_request = youtube.search().list(
                q=q, part="id", type="video", videoDuration="short",relevanceLanguage="en",
                publishedAfter=start_date, publishedBefore=end_date,
                maxResults=50, pageToken=next_page_token
            )
            search_response = search_request.execute()
            
            found_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            new_ids = [vid for vid in found_ids if vid not in existing_ids]

            if not new_ids:
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token: break
                continue

            # Llamada de detalles enriquecida
            v_res = youtube.videos().list(
                part="snippet,statistics,contentDetails,topicDetails,status",
                id=",".join(new_ids)
            ).execute()

            channel_ids = list(set([v['snippet']['channelId'] for v in v_res.get('items', [])]))
            subs_map = get_channel_subs(channel_ids)

            video_batch = []
            for video in v_res.get('items', []):
                snippet = video['snippet']
                title = snippet['title']
                
                if not is_wanted_language(title): continue
                
                content = video['contentDetails']
                # --- control if duration no exist ---
                raw_duration = content.get('duration')
                if not raw_duration:
                    continue # Si el video no tiene duración (error de API), lo saltamos
                    
                duration_sec = isodate.parse_duration(raw_duration).total_seconds()
                # ----------------------------
                raw_topics = video.get('topicDetails', {}).get('topicCategories', [])
                
                # Filtro de temática comida
                if duration_sec <= 60: #and any(t in str(raw_topics) for t in ["Food", "Cooking", "Cuisine", "Beverage"]):
                    stats = video['statistics']
                    views = int(stats.get('viewCount', 0))
                    likes = int(stats.get('likeCount', 0))
                    like_ratio = round(likes / views, 4) if views > 0 else 0

                    
                    comments = int(stats.get('commentCount', 0))
                    video_batch.append({
                        'video_id': video['id'],
                        'title': title,
                        'title_len': len(title),
                        'desc_len': len(snippet.get('description', '')),
                        'emoji_count': len(re.findall(r'[^\w\s,.]', title)),
                        'tag_count': len(snippet.get('tags', [])),
                        'published_hour': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')).hour,
                        'views': views,
                        'likes': likes,
                        'comments': comments,
                        'view_like_ratio': like_ratio, # Target para tu modelo
                        'channel_subs': subs_map.get(snippet['channelId'], 0),
                        'has_caption': 1 if content.get('caption') == 'true' else 0,
                        'definition': content.get('definition'), # hd o sd
                        'topic_categories': clean_topic_url(raw_topics),
                        'url': f"https://www.youtube.com/shorts/{video['id']}",
                        'engagement_rate': round((likes + comments * 3) / views * 100, 2) if views > 0 else 0,
                    })

                    
                    existing_ids.add(video['id'])

            if video_batch:
                df = pd.DataFrame(video_batch)
                df.to_csv(FILE_NAME, mode='a', index=False, header=not os.path.exists(FILE_NAME), encoding='utf-8-sig')
                total_new_videos += len(video_batch)

            next_page_token = search_response.get('nextPageToken')
            if not next_page_token: break
            
    print(f"🏁 Finalizado. Se han añadido {total_new_videos} videos nuevos al histórico.")

if __name__ == "__main__":
    get_shorts_massive()