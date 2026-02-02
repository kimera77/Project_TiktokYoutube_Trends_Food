# 📊 ETL Process - TikTok/YouTube Food Videos 2025

## 🎯 Objective
Clean and prepare the TikTok/YouTube 2025 dataset focused on **food content** for Power BI analysis and visualization.

---

## 📦 Data Source

The dataset is sourced from **Hugging Face** and contains short-form video trends from both TikTok and YouTube platforms throughout 2025. The original dataset includes approximately 60 columns with comprehensive metrics about video performance, creator information, temporal patterns, and engagement statistics across multiple countries and regions.

**Original Dataset**: Contains videos from various genres (Food, Gaming, Beauty, etc.)  
**Filtered Dataset**: Only videos categorized as "Food" genre for this project  
**Records**: ~1,790 food-related videos after filtering

---

## 🔧 ETL Process

### 1. Data Extraction
- Load dataset from Hugging Face using `datasets` library
- Initial exploration: 60+ columns with mixed data types
- Filter records where `genre` contains "Food"

### 2. Columns Removed
The following columns were identified as redundant or low-value for Power BI analysis:

**Duplicate columns**:
- `engagement_like_rate` → Duplicate of `like_rate`
- `engagement_comment_rate` → Duplicate of `comment_ratio`
- `engagement_share_rate` → Duplicate of `share_rate`

**Synthetic/low-value columns**:
- `sample_comments` → Synthetic comments with no analytical value
- `notes` → Empty or no description
- `source_hint` → No description available
- `trend_label` → No description available

**Technical columns**:
- `row_id` → MD5 hash used as primary key, not relevant for business analysis

**Total removed**: ~9 columns

### 3. Data Transformations

**Date Processing**:
- Convert `publish_date_approx` to datetime format
- Extract `year_month` for time-series aggregation
- Extract `publish_dayofweek` as readable day name
- Validate all dates are within 2025 range

**Filtering & Categorization**:
- Filter only videos where `genre` = "Food"
- Normalize `platform` values (TikTok/YouTube)
- Normalize `country` codes to ISO-2 uppercase format
- Standardize `device_type` values (Android/iOS/Web)

**Data Quality & Cleaning**:
- Remove records with `views = 0` (prevents division by zero errors)
- Validate `completion_rate` is between 0-1
- Validate `duration_sec` is within 5-90 seconds range
- Validate `upload_hour` is between 0-23
- Handle null values in critical columns
- Identify and remove duplicate records

**Calculated Metrics Validation**:
- Verify `engagement_per_1k` calculation
- Verify `engagement_rate` formula
- Verify `like_rate`, `comment_ratio`, `share_rate` calculations
- Ensure all engagement metrics are properly normalized

### 4. Final Dataset Structure (~40-45 columns)

**Dimensions** (for filtering and grouping):
- `platform`, `country`, `region`, `language`, `genre`, `category`
- `author_handle`, `creator_tier` (Micro/Mid/Macro/Star)
- `publish_date_approx`, `year_month`, `week_of_year`, `publish_dayofweek`, `publish_period`
- `device_type`, `device_brand`, `traffic_source`
- `event_season`, `season`, `is_weekend`

**Metrics** (for calculations and aggregations):
- **Views & Engagement**: `views`, `likes`, `comments`, `shares`, `saves`, `dislikes`
- **Duration & Watch Time**: `duration_sec`, `avg_watch_time_sec`, `completion_rate`
- **Engagement Metrics**: `engagement_total`, `engagement_per_1k`
- **Engagement Rates**: `like_rate`, `comment_ratio`, `share_rate`, `like_dislike_ratio`
- **Trend Metrics**: `trend_duration_days`, `engagement_velocity`
- **Creator Metrics**: `creator_avg_views`

**Metadata** (descriptive information):
- `title`, `title_length`, `has_emoji`, `hashtag`, `tags`

### 5. Data Export
- Save cleaned dataset as CSV with UTF-8 encoding for Power BI compatibility
- Ensure proper handling of special characters and emojis
- Optional: Create Excel file with multiple sheets (data + data dictionary)

---

## 📈 Key Metrics for Power BI Dashboards

### Primary KPIs:
- **Total Views**: Sum of all video views
- **Total Engagement**: Sum of likes + comments + shares + saves
- **Engagement Rate**: Average engagement as percentage of views
- **Completion Rate**: Average watch time vs. video duration
- **Average Watch Time**: Mean time users spend watching videos

### Suggested Analysis Dimensions:
- **Platform Comparison**: TikTok vs YouTube performance metrics
- **Geographic Trends**: Performance by country and region
- **Creator Performance**: Analysis by creator tier (Micro/Mid/Macro/Star)
- **Temporal Patterns**: Trends by day of week, hour, season, and special events
- **Device & Traffic**: Engagement by device type and traffic source
- **Content Analysis**: Title length, emoji usage, hashtag effectiveness

---

## 🚀 Implementation Steps

1. ✅ Load data from Hugging Face
2. ✅ Filter "Food" genre videos
3. ✅ Remove redundant and low-value columns
4. ✅ Data cleaning and quality validations
5. ✅ Date transformations and feature extraction
6. ✅ Export clean dataset to CSV for Power BI

---

## 📋 Files Generated
- `dataset_ML_food.csv` - Clean dataset ready for Power BI
- `DATA_DICTIONARY.csv` - Column definitions and descriptions
