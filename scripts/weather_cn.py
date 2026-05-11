#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国天气查询脚本 - 使用和风天气 API
国内访问速度快，无超时问题

支持：实时天气、天预报、空气质量、天气指数

用法：
    python3 weather_cn.py <城市> [上级行政区]
    
示例：
    python3 weather_cn.py 成都
    python3 weather_cn.py 成都 四川
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import gzip
from datetime import datetime

# ==================== 工具函数 ====================

def load_config():
    """从.env 文件加载配置，优先 ~/.hermes/.env，fallback 到本地 .env"""
    config = {}
    
    # 1. 优先读取 ~/.hermes/.env
    hermes_env = os.path.expanduser("~/.hermes/.env")
    for path in [hermes_env]:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            except:
                pass
    
    # 2. 本地 .env 作为 fallback（补充 ~/.hermes/.env 里没有的）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_env = os.path.join(script_dir, "../.env")
    if os.path.exists(local_env):
        try:
            with open(local_env, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        k = key.strip()
                        if k not in config:
                            config[k] = value.strip()
        except:
            pass
    
    return config


# ==================== 配置区 ====================

# 全局变量，延迟初始化
API_BASE = None
API_KEY = None

# 和风天气 API 端点（从.env 读取）
def get_api_base():
    """从.env 获取 API HOST"""
    config = load_config()
    api_host = config.get("QWEATHER_API_HOST")
    if not api_host:
        raise ValueError("未配置 QWEATHER_API_HOST")
    
    return api_host

def get_api_base_cached():
    """获取 API BASE（带缓存）"""
    global API_BASE
    if API_BASE is None:
        API_BASE = get_api_base()
    return API_BASE

def get_api_key():
    """获取 API Key"""
    # 1. 检查.env 文件
    config = load_config()
    if config.get("QWEATHER_API_KEY"):
        return config["QWEATHER_API_KEY"]
    else:
        raise ValueError("未配置 QWEATHER_API_KEY")

def get_api_key_cached():
    """获取 API KEY（带缓存）"""
    global API_KEY
    if API_KEY is None:
        API_KEY = get_api_key()
    return API_KEY

# ==================== 功能区 ====================

def get_city_info(city_name, adm=""):
    """获取城市信息（支持命令行传入城市名称或 ID，默认成都高新区）"""
    # 从本地缓存文件读取城市映射
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(script_dir, "../city_cache.json")
    city_map = {}
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                city_map = data.get("cities", {})
        except:
            pass
    
    # 查找缓存映射表
    city_info = city_map.get(f"{adm}-{city_name}")
    if city_info:
        return city_info
    
    # 如果没查到缓存，则调用 GeoAPI 查询
    city_info = fetch_city_coordinates(city_name, adm=adm)
    if not city_info:
        print(f"查询城市信息失败")
        return None

    # 保存到本地缓存文件
    city_map[f"{adm}-{city_name}"] = city_info
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump({"cities": city_map}, f, ensure_ascii=False, indent=4)
    
    return city_info

def fetch_api(endpoint, pathParams=None, queryParams=None):
    """通用 API 调用函数"""
    api_key = get_api_key_cached()
    if not api_key:
        print("未配置 API Key")
        return None
    
    api_base = get_api_base_cached()
    if not api_base:
        print("未配置 API Base")
        return None
    
    url = f"https://{api_base}/{endpoint}"
    if pathParams:
        url += f"/{pathParams}"
    
    if queryParams:
        url += f"?{queryParams}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header("X-QW-Api-Key", api_key)
        req.add_header("Accept-Encoding", "gzip")
        with urllib.request.urlopen(req, timeout=10) as response:
            # 处理 gzip 压缩
            if response.info().get('Content-Encoding') == 'gzip':
                data = json.loads(gzip.decompress(response.read()).decode('utf-8'))
            else:
                data = json.loads(response.read().decode('utf-8'))
            
            code = data.get("code", "")
            if code != "" and code != "200":
                print(f"错误：{data}")
                return None
            else:
                return data
    except Exception as e:
        print(f"错误：{e}")
        return None

def fetch_city_coordinates(city_name, adm=""):
    """根据城市名称查询经纬度（使用 GeoAPI）"""
    params = f"location={urllib.parse.quote(city_name)}"
    if adm:
        params += f"&adm={urllib.parse.quote(adm)}"

    result = fetch_api("geo/v2/city/lookup", queryParams=params)
    if not result:
        print(f"fetch_city_coordinates 失败")
        return None
    
    location = result.get("location")[0]
    return {
        "id": location.get("id"),
        "name": location.get("name"),
        "lat": location.get("lat"),
        "lon": location.get("lon"),
        "adm": location.get("adm1", "")
    }

def fetch_weather_now(location_id):
    """获取实时天气"""
    return fetch_api("v7/weather/now", queryParams=f"location={location_id}")

def fetch_weather_day(location_id):
    """获取当天天气"""
    result = fetch_api("v7/weather", pathParams="3d", queryParams=f"location={location_id}")
    if not result:
        print(f"fetch_weather_day 获取失败")
        return None
    
    return result.get("daily")[0]

def fetch_weather_3d_full(location_id):
    """获取 3 天天气预报（完整）"""
    return fetch_api("v7/weather", pathParams="3d", queryParams=f"location={location_id}")
    

def fetch_weather_3d(location_id):
    """获取 3 天天气预报"""
    return fetch_api("v7/weather", pathParams="3d", queryParams=f"location={location_id}")

def fetch_air_quality_now(latitude, longitude):
    """获取空气质量"""
    return fetch_api("airquality/v1/current", pathParams=f"{latitude}/{longitude}")

def fetch_air_quality_hourly(latitude, longitude):
    """获取空气质量"""
    return fetch_api("airquality/v1/hourly", pathParams=f"{latitude}/{longitude}")

def fetch_indices(location_id):
    """获取天气指数"""
    return fetch_api("v7/indices", pathParams=f"1d", queryParams=f"type=0&location={location_id}")


def main():
    """主函数"""

    # 从命令行获取city和adm参数
    if len(sys.argv) < 2:
        print("用法: python script.py <city_name> [adm]")
        sys.exit(1)
    
    city_name = sys.argv[1]
    adm = sys.argv[2] if len(sys.argv) > 2 else ""

    # 获取城市信息（city_id, city_name）
    city_info = get_city_info(city_name, adm)
    if not city_info:
        print(f"未找到城市:{city_name}, {adm}")
        return
    
    location_id = city_info.get("id")
    latitude, longitude = city_info.get("lat"), city_info.get("lon")
    
    # 获取所有数据
    now_data = fetch_weather_now(location_id)
    forecast_data = fetch_weather_day(location_id)
    forecast_3d_data = fetch_weather_3d_full(location_id)
    air_data = fetch_air_quality_hourly(latitude, longitude)
    indices_data = fetch_indices(location_id)
    
    # 生成报告
    report = {
        "city_name": city_name,
        "adm": adm,
        "now_weather": now_data,
        "forecast_weather": forecast_data,
        "forecast_3d": forecast_3d_data,
        "air_quality": air_data,
        "indices": indices_data
    }
    print(report)

if __name__ == "__main__":
    main()
