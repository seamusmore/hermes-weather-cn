# Weather-CN Data Source Catalogue

Catalogue of public weather data sources validated in unattended/cron mode.
Used by the Fallback Workflow when the native script is blocked by security policy.

## Tier 1: Reliable & Comprehensive

### 1. 中国天气网 (weather.com.cn)
- **URL pattern**: `https://www.weather.com.cn/weather/{cityCode}.shtml`
- **City codes**: 成都=101270101, 绵阳=101270401, 杭州=101210101
- **Data**: 7-day forecast, day/night conditions, temp highs/lows, wind, life indices (穿衣/运动/洗车/紫外线/感冒)
- **Reliability**: High. Official CMA portal. Rarely fails.
- **Tip**: Also try `weather1d/{code}.shtml` for today/night split view.

### 2. 中国气象局官方逐小时 (weather.cma.cn)
- **URL pattern**: `https://weather.cma.cn/web/weather/{stationId}.html`
- **Station IDs**: 成都=S1003
- **Data**: 3-hourly granular forecast — temp, precipitation (mm), wind speed/direction, pressure (hPa), humidity (%), cloud cover (%)
- **Reliability**: High. Best source for precise departure-time temperature and humidity.
- **Tip**: Look for tables with 08:00, 11:00, 14:00, 17:00, 20:00, 23:00, 02:00, 05:00 columns.

### 3. 墨迹天气 (Moji Weather)
- **URL pattern**: `https://tianqi.moji.com/today/china/{province}/{city}`
- **Example**: `https://tianqi.moji.com/today/china/sichuan/chengdu`
- **Data**: Real-time temp, weather condition, humidity, wind; 15-day forecast; rich life indices (UV, comfort, exercise, car wash, cold risk, fishing, etc.)
- **Reliability**: High. Clean structured data.
- **Tip**: Good fallback when qweather indices are sparse.

## Tier 2: Specialized (AQI / Indices)

### 4. 空气知音 (air-level.com)
- **URL pattern**: `https://www.air-level.com/air/{city}/`
- **Example**: `https://www.air-level.com/air/chengdu/`
- **Data**: AQI, PM2.5, PM10, NO2, per-station breakdown
- **Reliability**: High. Simple HTML tables.

### 5. AQICN (aqicn.org)
- **URL pattern**: `https://aqicn.org/city/{city}/cn/`
- **Example**: `https://aqicn.org/city/chengdu/cn/`
- **Data**: US EPA AQI standard, hourly pollutant breakdown (PM2.5, PM10, O3, NO2, SO2, CO), meteorological data (temp, humidity, pressure, wind)
- **Reliability**: High. Good for cross-checking AQI against Chinese standards.

### 6. 和风天气指数 (qweather.com)
- **URL pattern**: `https://www.qweather.com/indices/{city}-{code}.html`
- **Example**: `https://www.qweather.com/indices/chengdu-101270101.html`
- **Data**: Daily life indices (舒适度, 洗车, 穿衣, 感冒, 运动, 旅游, 紫外线, 空气污染扩散)
- **Reliability**: Medium-High. Sometimes page structure changes.

## Tier 3: Supplemental / Long-range

### 7. Weather-Forecast.com
- **URL pattern**: `https://zh.weather-forecast.com/locations/{City}/forecasts/latest`
- **Example**: `https://zh.weather-forecast.com/locations/Chengdu/forecasts/latest`
- **Data**: 16-day forecast in 3-day chunks, rainfall totals, hourly granularity for near-term
- **Reliability**: Medium. Good for validating multi-day trends.

### 8. Ventusky
- **URL pattern**: `https://www.ventusky.com/zh/{city}`
- **Example**: `https://www.ventusky.com/zh/chengdu`
- **Data**: Visual maps, hourly temp/precip/wind/humidity, AQI overlay
- **Reliability**: Medium. Heavy JS; extraction may be partial.

## Known Failing Sources

| Source | URL | Failure Mode |
|--------|-----|--------------|
| Baidu Weather | `weathernew.pae.baidu.com/...` | `Failed to fetch url` — blocked or requires JS |
| Weaoo | `www.weaoo.com/...` | `Failed to fetch url` — blocked or geo-restricted |

## Cross-Referencing Strategy

1. **Forecast**: weather.com.cn (7-day) + CMA hourly (precision)
2. **AQI**: air-level.com + aqicn.org (cross-check Chinese vs US standards)
3. **Indices**: qweather.com + moji.com (complement each other)
4. **Validation**: weather-forecast.com (long-range trend check)

## AQI Reference

| AQI | 等级 | 健康建议 |
|-----|------|------------|
| 0-50 | 优 | 空气质量令人满意，基本无污染 |
| 51-100 | 良 | 可正常活动 |
| 101-150 | 轻度污染 | 敏感人群减少外出 |
| 151-200 | 中度污染 | 所有人减少户外活动 |
| 201-300 | 重度污染 | 所有人避免户外活动 |
| >300 | 严重污染 | 所有人留在室内 |
