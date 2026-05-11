# weather-cn

中国天气查询技能，使用和风天气 API，国内访问速度快。

## Features

- 实时天气查询
- 3 天天气预报
- 空气质量（AQI / PM2.5）
- 生活指数（紫外线、穿衣、洗车、感冒、过敏、钓鱼等）

## Installation

### Recommended (via Hermes CLI)

```bash
hermes skills install https://github.com/seamusmore/hermes-weather-cn.git
```

Then restart the gateway for the skill to take effect.

### Manual (alternative)

```bash
# Clone into Hermes skills directory
git clone https://github.com/seamusmore/hermes-weather-cn.git \
  ~/.hermes/skills/openclaw-imports/weather-cn
```

## Configuration

在 `~/.hermes/.env` 中配置 API 密钥：

```bash
QWEATHER_API_HOST=your_api_host
QWEATHER_API_KEY=your_api_key
```

申请 API Key: https://dev.qweather.com/

## Usage

### 脚本直接调用

```bash
# 查询城市天气
python3 scripts/weather_cn.py 成都

# 指定上级行政区（避免重名）
python3 scripts/weather_cn.py 高新区 成都
python3 scripts/weather_cn.py 成都 四川
```

### Hermes 技能调用

技能名: `weather-cn`

自然语言触发：
- "成都天气怎么样"
- "今天会下雨吗"
- "明天温度多少度"

## AQI 等级说明

| AQI | 等级 | 建议 |
|-----|------|------|
| 0-50 | 优 | 空气质量令人满意 |
| 51-100 | 良 | 可正常活动 |
| 101-150 | 轻度污染 | 敏感人群减少外出 |
| 151-200 | 中度污染 | 所有人减少户外活动 |
| 201-300 | 重度污染 | 所有人避免户外活动 |
| >300 | 严重污染 | 所有人留在室内 |

## License

MIT
