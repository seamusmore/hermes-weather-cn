---
name: weather-cn
description: 中国天气查询（国内访问速度快）
author: Luna
version: 1.0.0
triggers:
  - "天气"
  - "天气预报"
  - "天气提醒"
  - "weather"
---

# 中国天气查询 (weather-cn)

查询中国城市天气，国内访问速度快，无超时问题。

## Installation

### 推荐（via Hermes CLI）

```bash
hermes skills install https://github.com/seamusmore/hermes-weather-cn.git
```

Then restart the gateway for the skill to take effect.

### 手动

```bash
# Clone into Hermes skills directory
git clone https://github.com/seamusmore/hermes-weather-cn.git \
  ~/.hermes/skills/openclaw-imports/weather-cn
```

## Configuration

在 `~/.hermes/.env` 中配置和风天气 API：

```bash
QWEATHER_API_HOST=your_api_host
QWEATHER_API_KEY=your_api_key
```

申请 API Key：https://dev.qweather.com/

## 脚本调用

本 skill 包含可执行脚本 `weather_cn.py`，位于 `scripts/` 子目录下：

**指定城市（传入城市名称和上级行政区名称）**：
```bash
# 按城市名称查询（从本地缓存读取城市 ID）
python3 {baseDir}/scripts/weather_cn.py 北京

# 按城市名称+上级行政区名称查询（避免城市重名）
python3 {baseDir}/scripts/weather_cn.py 高新区 成都
python3 {baseDir}/scripts/weather_cn.py 成都 四川
```

**AQI 等级说明**：
| AQI | 等级 | 建议 |
|-----|------|------|
| 0-50 | 优 | 空气质量令人满意，基本无污染 |
| 51-100 | 良 | 可正常活动 |
| 101-150 | 轻度污染 | 敏感人群减少外出 |
| 151-200 | 中度污染 | 所有人减少户外活动 |
| 201-300 | 重度污染 | 所有人避免户外活动 |
| >300 | 严重污染 | 所有人留在室内 |

**指数类型代码**：
| type | 指数名称 | 说明 |
|------|----------|------|
| 1 | 紫外线指数 | 0-5 级，数值越大越强 |
| 3 | 穿衣指数 | 0-8 级，数值越大穿得越多 |
| 6 | 洗车指数 | 0-4 级，数值越小越适宜 |
| 7 | 感冒指数 | 0-4 级，数值越大越易感冒 |
| 8 | 过敏指数 | 0-4 级，数值越大越易过敏 |
| 11 | 钓鱼指数 | 0-4 级，数值越大越适宜 |

## 错误码

| 代码 | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 请求错误 |
| 401 | 认证失败（key 错误） |
| 402 | 超出访问次数 |
| 403 | 无访问权限 |
| 404 | 数据不存在 |
| 429 | 访问过于频繁 |
| 500 | 无响应或超时 |

## 注意事项

1. 免费版 API 每日有访问次数限制（通常够用）
2. 建议缓存查询结果，避免频繁调用
3. API Key 不要公开分享（存 ~/.hermes/.env，不上传到仓库）
4. 国内访问速度快，一般 1-2 秒返回

## Pitfalls

- **Security scan blocks script execution**: In headless or cron environments, running `python3 weather_cn.py` triggers a security scan (`tirith:unknown`) and blocks with `approval_required`. Direct `curl` calls to the API endpoint are also blocked.
  - *Symptom*: `exit_code: -1`, `status: approval_required`, `pattern_key: tirith:unknown`.
  - *Do not retry or attempt the script in unattended mode* — approval cannot be obtained. Proceed immediately to the Fallback Workflow.

## Fallback Workflow (Unattended / Cron Mode)

When the script or curl is blocked by security policy, use `web_search` + `web_extract` to gather weather data from public authoritative sources. Based on proven session results, query these specific pages:

1. **Current conditions + 7-day forecast**:
   - Search: `成都 天气预报 site:weather.com.cn` (e.g., `https://www.weather.com.cn/weather/101270101.shtml`)
   - Extract: current temp range, weather phenomenon, humidity, wind, and 3-day forecast highs/lows.
   - *City codes*: 成都 is `101270101`; 绵阳 is `101270401`.

2. **Real-time AQI / PM2.5**:
   - `https://www.air-level.com/air/chengdu/` — clean tables for AQI, PM2.5, PM10, station breakdown.
   - `https://aqicn.org/city/chengdu/cn/` — US EPA AQI standard with hourly history.
   - Search: `成都 AQI PM2.5 实时` to cross-check.

3. **Detailed life indices (穿衣/洗车/紫外线/感冒/运动/旅游/过敏/钓鱼)**:
   - `https://www.qweather.com/indices/chengdu-101270101.html` — structured daily indices for ~7 days.

4. **Compile report** using the canonical template below. Determine if extreme weather exists (暴雨, 暴雪, 台风, 雾霾, <0°C or >35°C). Provide contextual 出门建议 based on the user's wake-up and departure times.

### Canonical Report Template

```text
☀️ 天气提醒：[天气概述]，气温 [最低]°C 至 [最高]°C。[出门建议]

📍 地点：[城市]
🌡️ 当前：[温度]°C [天气状况]
💧 湿度：[湿度]%
🍃 风向：[风向][风力] 级

🌫️ 空气质量：[AQI] - [类别]
  [健康建议]

📋 生活建议：
  [穿衣建议]
  [感冒/过敏/紫外线指数等]
```

- Use `至` for temperature ranges (e.g., `17°C 至 31°C`).
- If the user specifies wake-up and departure times (e.g., 7:10 wake / 8:00 leave), tailor 出门建议 to that exact window.
