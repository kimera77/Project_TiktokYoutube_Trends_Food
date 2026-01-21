# 📊 ETL - TikTok/YouTube 2025 Dataset

## 🎯 OBJECTIVE
Clean and prepare the TikTok/YouTube 2025 dataset focused on **food** content for Power BI analysis.

---

## 🗑️ 1. COLUMNS TO DROP (Redundant or Unnecessary)

### Duplicate/redundant columns:
- `engagement_rate` → Keep the specific ones (like_rate, comment_ratio, etc.)
- `engagement_like_rate` → **DUPLICATE** of `like_rate`
- `engagement_comment_rate` → **DUPLICATE** of `comment_ratio`
- `engagement_share_rate` → **DUPLICATE** of `share_rate`

### Synthetic/low-value columns for Power BI:
- `sample_comments` → Synthetic comments with no analytical value
- `notes` → No description, likely empty
- `source_hint` → No description
- `trend_label` → No description

### Unnecessary technical columns:
- `row_id` → MD5 primary key, doesn't contribute to business metrics

**Total to drop: ~9 columns**

---

## 🔧 2. TRANSFORMATIONS AND CLEANING

### Dates:
- Convert `publish_date_approx` to datetime type
- Extract month, readable day of week
- Validate that all dates are within 2025

### Categorization:
- **Filter only food videos**: `genre` contains "Food" or related categories
- Normalize `platform`: Verify unique values (TikTok/YouTube)
- Normalize `country`: ISO-2 codes in uppercase
- `device_type`: Group if inconsistent values exist

### Clean calculated metrics:
- `completion_rate`: Validate between 0-1 (or 0-100%)
- `engagement_per_1k`: Verify correct calculation
- Remove rows with `views = 0` (division by zero)

### Duplicates:
- Validate duplicates by `row_id` or key field combination

---

## ✅ 3. QUALITY VALIDATIONS

- **Nulls**: Identify and handle null values in key columns
- **Outliers**: Detect atypical values in views, likes, duration_sec
- **Valid ranges**: 
  - `duration_sec`: 5-90 seconds
  - `upload_hour`: 0-23
  - `week_of_year`: 1-53
  - `engagement_rate`: 0-1

---

## 📊 4. FINAL COLUMNS OPTIMIZED FOR POWER BI

### Main dimensions:
- `platform`, `country`, `region`, `language`, `genre`, `category`
- `author_handle`, `creator_tier`
- `publish_date_approx`, `year_month`, `week_of_year`, `publish_dayofweek`, `publish_period`
- `device_type`, `device_brand`, `traffic_source`
- `event_season`, `season`, `is_weekend`

### Main metrics:
- `views`, `likes`, `comments`, `shares`, `saves`, `dislikes`
- `duration_sec`, `avg_watch_time_sec`, `completion_rate`
- `engagement_total`, `engagement_per_1k`
- `like_rate`, `comment_ratio`, `share_rate`, `like_dislike_ratio`
- `trend_duration_days`, `engagement_velocity`
- `creator_avg_views`

### Metadata:
- `title`, `title_length`, `has_emoji`, `hashtag`, `tags`

**Estimated: ~40-45 useful columns** (vs ~60 original)

---

## 💾 5. EXPORT

- Save clean CSV for Power BI
- Optional: Create Excel with multiple sheets (data + dictionary)
- UTF-8 encoding for special characters

---

## 📝 DICCIONARIO DE DATOS

| Column | Description |
|--------|-------------|
| platform | Platform (TikTok/YouTube) |
| country | Country ISO-2 code |
| region | Region macro label (if available) |
| language | Primary language inferred from country (fallback to 'en') |
| category | Video category (if available) |
| hashtag | Primary hashtag aligned with genre |
| title_keywords | Short realistic title-like keywords |
| author_handle | Creator handle/channel (brand-like, synthetic) |
| sound_type | Sound type (if present) |
| music_track | Music track (if present) |
| week_of_year | ISO week number (1–53) |
| duration_sec | Shorts-style duration in seconds (TikTok ~5–75, YouTube ~5–90) |
| views | Total views |
| likes | Likes count |
| comments | Comments count |
| shares | Shares count |
| saves | Saves count |
| engagement_rate | (likes+comments+shares+saves) / views |
| trend_label | No description available |
| source_hint | No description available |
| notes | No description available |
| device_type | Android/iOS/Web |
| upload_hour | Hour of day video published (0–23) |
| genre | Canonical content genre |
| trend_duration_days | Days the video remained trending (synthetic) |
| trend_type | Short (≤7), Medium (8–21), Evergreen (≥22) |
| engagement_velocity | views / trend_duration_days |
| dislikes | Dislikes (synthetic, platform-aware) |
| comment_ratio | comments / views |
| share_rate | shares / views |
| save_rate | saves / views |
| like_dislike_ratio | likes / (dislikes+1) |
| publish_dayofweek | Day of week of publish_date |
| publish_period | Part of day bucket (Morning/Afternoon/Evening/Night) |
| event_season | Seasonal/contextual event (Ramadan, SummerBreak, BackToSchool, HolidaySeason, None) |
| tags | YouTube-like comma-separated tags aligned with genre |
| sample_comments | One short synthetic multilingual comment |
| creator_avg_views | Avg views per video for the creator (across dataset rows) |
| creator_tier | Creator tier based on avg views: Micro / Mid / Macro / Star |
| season | Climatological season (Winter/Spring/Summer/Fall) |
| publish_date_approx | ISO date reconstructed/approximated within 2025 (clipped to 2025-09-12) |
| year_month | Publish year-month for time-series aggregation |
| title | Short realistic video title (synthetic) |
| title_length | Character count of title |
| has_emoji | Whether title contains emoji (1/0) |
| avg_watch_time_sec | Estimated average watch time (seconds) |
| completion_rate | avg_watch_time_sec / duration_sec |
| device_brand | If mobile: device brand (iPhone, Samsung, Huawei, Xiaomi, Oppo, Vivo, Pixel, Other); Web → Desktop |
| traffic_source | Coarse discovery source (TikTok: ForYou/Following/Search/External; YouTube: Home/Suggested/Search/External) |
| is_weekend | Publish on Fri/Sat/Sun = 1 |
| row_id | Deterministic MD5 over [platform, country, author_handle, title, publish_date_approx, duration_sec] (primary key) |
| engagement_total | likes + comments + shares + saves |
| like_rate | likes / views |
| dislike_rate | dislikes / views |
| engagement_per_1k | Total engagements per 1,000 views |
| engagement_like_rate | Likes divided by Views; NaN when Views <= 0 |
| engagement_comment_rate | Comments divided by Views; NaN when Views <= 0 |
| engagement_share_rate | Shares divided by Views; NaN when Views <= 0 |

---

## 🚀 IMPLEMENTATION STEPS

1. ✅ Load data from Hugging Face
2. ✅ Filter "Food" genre
3. ✅ Remove redundant columns
4. ✅ Data cleaning and quality validations
5. ✅ Date and category transformations
6. ✅ Export to CSV/Excel for Power BI

---

## 📈 KEY METRICS FOR POWER BI

### Main KPIs:
- Total Views
- Total Engagement (likes + comments + shares + saves)
- Engagement Rate
- Completion Rate
- Average Watch Time

### Suggested Analysis:
- TikTok vs YouTube comparison
- Trending by country/region
- Performance by creator_tier
- Temporal patterns (day of week, hour, season)
- Engagement by device type and traffic source
