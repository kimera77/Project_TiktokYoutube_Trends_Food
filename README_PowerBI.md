# 📊 POWER BI - TikTok/YouTube Food Trends Analysis

## 🎯 OBJETIVO DEL PROYECTO
Crear un dashboard interactivo en Power BI para analizar tendencias de contenido de **comida** en TikTok y YouTube durante 2025, identificando patrones de engagement, comportamiento de creadores y oportunidades de contenido.

---

## 📥 1. TRATAMIENTO DE DATOS EN POWER BI
DimDate = 
ADDCOLUMNS (
    CALENDAR (DATE(2025,1,1), DATE(2025,12,31)),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "Month Name", FORMAT([Date], "MMMM"),
    "Quarter", "Q" & FORMAT([Date], "0"),
    "Week", WEEKNUM([Date], 2),
    "Day", DAY([Date]),
    "Day Name", FORMAT([Date], "dddd"),
    "DayOfWeek", WEEKDAY([Date], 2)
)

**B. Categorización de métricas de engagement**
```powerquery
// Crear columnas condicionales para segmentar engagement
= Table.AddColumn(PreviousStep, "Engagement Level", each 
    if [engagement_rate] >= 0.15 then "High"
    else if [engagement_rate] >= 0.08 then "Medium"
    else "Low")

// Categorizar duración de videos
= Table.AddColumn(PreviousStep, "Duration Category", each 
    if [duration_sec] <= 15 then "Ultra Short (≤15s)"
    else if [duration_sec] <= 30 then "Short (16-30s)"
    else if [duration_sec] <= 60 then "Medium (31-60s)"
    else "Long (>60s)")
```

**C. Normalización de plataformas**
```powerquery
// Asegurar valores consistentes
= Table.TransformColumns(PreviousStep, {
    {"platform", each Text.Upper(Text.Trim(_)), type text},
    {"country", each Text.Upper(Text.Trim(_)), type text}
})
```

### 1.3 Modelo de Datos (Star Schema)

**Tablas de Dimensiones:**
- `DimDate` (Calendario)
- `DimPlatform` (TikTok, YouTube)
- `DimCountry` (País, Región)
- `DimCreator` (author_handle, creator_tier)
- `DimContent` (genre, category, hashtag)
- `DimDevice` (device_type, device_brand)

**Tabla de Hechos:**
- `FactVideos` (métricas: views, likes, comments, shares, etc.)

**Relaciones:**
- `FactVideos[publish_date_approx]` → `DimDate[Date]` (1:N)
- `FactVideos[platform]` → `DimPlatform[platform]` (N:1)
- `FactVideos[country]` → `DimCountry[country]` (N:1)
- `FactVideos[author_handle]` → `DimCreator[author_handle]` (N:1)

---

## 💻 2. CÓDIGO DAX - MEDIDAS CLAVE

### 2.1 Medidas Básicas de Agregación

```dax
// Total de Visualizaciones
Total Views = SUM(FactVideos[views])

// Total de Engagement
Total Engagement = 
    SUM(FactVideos[likes]) + 
    SUM(FactVideos[comments]) + 
    SUM(FactVideos[shares]) + 
    SUM(FactVideos[saves])

// Promedio de Engagement Rate
Avg Engagement Rate = AVERAGE(FactVideos[engagement_rate])

// Total de Videos
Total Videos = COUNTROWS(FactVideos)

// Total de Creadores
Total Creators = DISTINCTCOUNT(FactVideos[author_handle])
```

### 2.2 Medidas Avanzadas - Time Intelligence

```dax
// Views del Mes Anterior
Views Previous Month = 
CALCULATE(
    [Total Views],
    DATEADD(DimDate[Date], -1, MONTH)
)

// Crecimiento MoM (Month over Month)
Views Growth MoM = 
VAR CurrentMonth = [Total Views]
VAR PreviousMonth = [Views Previous Month]
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0)

// Acumulado Year-to-Date
Views YTD = 
CALCULATE(
    [Total Views],
    DATESYTD(DimDate[Date])
)

// Promedio Móvil 7 días
Views 7-Day Moving Avg = 
CALCULATE(
    [Total Views],
    DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -7, DAY)
) / 7
```

### 2.3 Medidas de Rendimiento Comparativo

```dax
// Tasa de Engagement vs Promedio
Engagement vs Average = 
VAR AvgEngagement = CALCULATE([Avg Engagement Rate], ALL(FactVideos))
VAR CurrentEngagement = [Avg Engagement Rate]
RETURN
    DIVIDE(CurrentEngagement - AvgEngagement, AvgEngagement, 0)

// Participación de Mercado por Plataforma
Platform Market Share = 
DIVIDE(
    [Total Views],
    CALCULATE([Total Views], ALL(FactVideos[platform])),
    0
)

// Ranking de Creadores
Creator Rank = 
RANKX(
    ALL(FactVideos[author_handle]),
    [Total Views],
    ,
    DESC,
    DENSE
)

// Top 10% de Videos
Is Top 10% = 
VAR TotalVideos = [Total Videos]
VAR CurrentRank = 
    RANKX(
        ALL(FactVideos),
        [Total Views],
        ,
        DESC,
        DENSE
    )
RETURN
    IF(CurrentRank <= TotalVideos * 0.1, "Top 10%", "Others")
```

### 2.4 Medidas de Eficiencia de Contenido

```dax
// Engagement por 1,000 vistas (calculado)
Engagement Per 1K = 
DIVIDE([Total Engagement], [Total Views], 0) * 1000

// Tasa de Retención Promedio
Avg Retention Rate = AVERAGE(FactVideos[completion_rate])

// Tiempo Promedio de Visualización
Avg Watch Time = AVERAGE(FactVideos[avg_watch_time_sec])

// Ratio de Interacción (comentarios/likes)
Comment to Like Ratio = 
DIVIDE(
    SUM(FactVideos[comments]),
    SUM(FactVideos[likes]),
    0
)

// Viralidad Score (combinación de shares y engagement)
Virality Score = 
([Total Shares] / [Total Videos]) * [Avg Engagement Rate] * 100
```

### 2.5 Medidas de Segmentación

```dax
// Videos de Alto Rendimiento
High Performance Videos = 
CALCULATE(
    [Total Videos],
    FactVideos[engagement_rate] >= 0.15
)

// % de Videos Virales (>1M views)
Viral Video % = 
DIVIDE(
    CALCULATE([Total Videos], FactVideos[views] >= 1000000),
    [Total Videos],
    0
)

// Engagement por Tipo de Creador
Creator Tier Engagement = 
SWITCH(
    TRUE(),
    SELECTEDVALUE(FactVideos[creator_tier]) = "Star", [Avg Engagement Rate],
    SELECTEDVALUE(FactVideos[creator_tier]) = "Macro", [Avg Engagement Rate],
    SELECTEDVALUE(FactVideos[creator_tier]) = "Mid", [Avg Engagement Rate],
    [Avg Engagement Rate]
)
```

### 2.6 Medidas de Análisis Temporal

```dax
// Mejor Día de la Semana (por engagement)
Best Day of Week = 
VAR BestDay = 
    MAXX(
        VALUES(FactVideos[publish_dayofweek]),
        CALCULATE([Avg Engagement Rate])
    )
RETURN
    CALCULATE(
        MAX(FactVideos[publish_dayofweek]),
        FILTER(
            ALL(FactVideos[publish_dayofweek]),
            [Avg Engagement Rate] = BestDay
        )
    )

// Estacionalidad - Comparación con mismo mes año anterior
YoY Comparison = 
VAR CurrentPeriod = [Total Views]
VAR SamePeriodLastYear = 
    CALCULATE(
        [Total Views],
        DATEADD(DimDate[Date], -1, YEAR)
    )
RETURN
    DIVIDE(CurrentPeriod - SamePeriodLastYear, SamePeriodLastYear, 0)
```

---

## 📊 3. PREGUNTAS DE NEGOCIO Y VISUALIZACIONES

### 3.1 Análisis de Plataforma

**Pregunta:** ¿Qué plataforma genera más engagement en contenido de comida?

**Visualizaciones:**
- **Gráfico de Barras Apiladas**: Views y Engagement por plataforma
- **KPI Cards**: Total Views TikTok vs YouTube
- **Gráfico de Líneas**: Tendencia temporal de engagement por plataforma
- **Treemap**: Distribución de categorías por plataforma

**Métricas clave:**
- Platform Market Share
- Avg Engagement Rate
- Total Videos

---

### 3.2 Análisis Geográfico

**Pregunta:** ¿Qué países/regiones tienen mejor rendimiento en videos de comida?

**Visualizaciones:**
- **Mapa de Calor**: Views por país
- **Gráfico de Barras Horizontal**: Top 10 países por engagement
- **Tabla Matriz**: País × Plataforma con métricas
- **Scatter Plot**: Views vs Engagement Rate por país

**Métricas clave:**
- Total Views
- Avg Engagement Rate
- Total Creators

---

### 3.3 Análisis de Creadores

**Pregunta:** ¿Qué tier de creadores genera más valor?

**Visualizaciones:**
- **Gráfico de Columnas Agrupadas**: Avg Views por creator_tier
- **Funnel Chart**: Distribución de creadores por tier
- **Tabla con Sparklines**: Top 20 creadores con tendencia temporal
- **Gráfico de Dispersión**: Followers vs Engagement

**Métricas clave:**
- Creator Rank
- Avg Views per Creator
- Creator Tier Engagement

---

### 3.4 Análisis Temporal

**Pregunta:** ¿Cuándo es el mejor momento para publicar contenido de comida?

**Visualizaciones:**
- **Matriz de Calor**: Día de semana × Hora del día (engagement)
- **Gráfico de Líneas**: Tendencia semanal de views
- **Gráfico de Áreas**: Distribución por publish_period
- **Ribbon Chart**: Evolución de categorías a lo largo del año

**Métricas clave:**
- Best Day of Week
- Views 7-Day Moving Avg
- YoY Comparison

---

### 3.5 Análisis de Contenido

**Pregunta:** ¿Qué tipo de contenido funciona mejor?

**Visualizaciones:**
- **Gráfico de Barras**: Engagement por duration_category
- **Word Cloud**: Hashtags más populares
- **Gráfico de Columnas**: Avg Retention Rate por género
- **Waterfall Chart**: Contribución de cada tipo de engagement

**Métricas clave:**
- Engagement Per 1K
- Avg Retention Rate
- Virality Score

---

### 3.6 Análisis de Dispositivos y Tráfico

**Pregunta:** ¿Desde dónde consumen el contenido los usuarios?

**Visualizaciones:**
- **Donut Chart**: Distribución por device_type
- **Gráfico de Barras Apiladas**: Traffic source × Platform
- **Sankey Diagram**: Flujo de device_type → traffic_source → engagement level

**Métricas clave:**
- Total Views
- Avg Engagement Rate
- Avg Watch Time

---

## 📈 4. ESTRUCTURA DEL DASHBOARD

### Página 1: EXECUTIVE OVERVIEW
- KPIs principales (Total Views, Engagement, Videos, Creators)
- Tendencia mensual de views
- Comparación TikTok vs YouTube
- Top 5 países

### Página 2: PLATFORM DEEP DIVE
- Análisis detallado por plataforma
- Engagement metrics breakdown
- Distribución de categorías
- Performance por creator_tier

### Página 3: GEOGRAPHIC ANALYSIS
- Mapa interactivo
- Top performers por región
- Tabla de métricas por país
- Comparación regional

### Página 4: CREATOR INSIGHTS
- Ranking de creadores
- Distribución por tier
- Análisis de contenido por creador
- Engagement trends

### Página 5: TEMPORAL PATTERNS
- Matriz día/hora
- Best times to post
- Seasonal trends
- Week-over-week analysis

### Página 6: CONTENT OPTIMIZATION
- Duration analysis
- Hashtag performance
- Retention metrics
- Engagement breakdown

---

## 🎨 5. MEJORES PRÁCTICAS DE DISEÑO

### 5.1 Paleta de Colores
```
TikTok: #000000, #69C9D0, #EE1D52
YouTube: #FF0000, #282828, #FFFFFF
Engagement Levels: 
  - High: #00C851
  - Medium: #FFB400
  - Low: #FF4444
```

### 5.2 Jerarquía Visual
- KPIs en la parte superior
- Gráficos principales en el centro
- Filtros en panel lateral izquierdo
- Detalles en tooltips

### 5.3 Interactividad
- Filtros sincronizados entre páginas
- Drill-through desde overview a detalles
- Tooltips enriquecidos con métricas adicionales
- Bookmarks para vistas predefinidas

---

## 🚀 6. IMPLEMENTACIÓN

### Paso 1: Preparación
1. Cargar `food_videos_2025_clean.csv` en Power BI Desktop
2. Crear tabla de calendario (DimDate)
3. Establecer relaciones del modelo estrella

### Paso 2: DAX
1. Crear medidas básicas
2. Implementar Time Intelligence
3. Añadir medidas calculadas complejas

### Paso 3: Visualizaciones
1. Crear página Executive Overview
2. Desarrollar páginas de análisis detallado
3. Configurar interactividad y filtros

### Paso 4: Testing
1. Validar cálculos DAX
2. Verificar rendimiento del dashboard
3. Optimizar consultas lentas

### Paso 5: Publicación
1. Publicar en Power BI Service
2. Configurar actualización automática
3. Compartir con stakeholders

---

## 📚 7. RECURSOS DE APRENDIZAJE DAX

### Conceptos Fundamentales
1. **Context (Row Context vs Filter Context)**
2. **CALCULATE y FILTER**
3. **Time Intelligence Functions**
4. **Variables (VAR)**
5. **Iterator Functions (SUMX, AVERAGEX)**

### Tutoriales Recomendados
- [SQLBI - DAX Guide](https://dax.guide/)
- [Microsoft Learn - DAX Basics](https://learn.microsoft.com/power-bi/dax/)
- [Guy in a Cube - YouTube Channel](https://www.youtube.com/c/GuyinaCube)

### Ejercicios Prácticos
1. Crear medidas de comparación temporal (MoM, YoY)
2. Implementar rankings dinámicos
3. Calcular promedios móviles
4. Crear segmentaciones condicionales

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Cargar y limpiar datos en Power Query
- [ ] Crear modelo de datos (Star Schema)
- [ ] Implementar tabla de calendario
- [ ] Crear 20+ medidas DAX
- [ ] Diseñar 6 páginas de dashboard
- [ ] Configurar interactividad y filtros
- [ ] Validar cálculos y rendimiento
- [ ] Documentar medidas DAX
- [ ] Publicar en Power BI Service
- [ ] Capacitar usuarios finales

---

**Autor:** Joaquim  
**Fecha:** Enero 2026  
**Versión:** 1.0
