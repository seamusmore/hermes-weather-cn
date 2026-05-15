#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国天气查询脚本 - 使用和风天气 API
国内访问速度快，无超时问题

支持：实时天气、天预报、空气质量、天气指数

用法：
    python3 weather_cn.py --name 城市 [--adm 上级行政区]
    python3 weather_cn.py --lat <lat> --lon <lon> [--name city_name]
    
示例：
    python3 weather_cn.py --name 成都
    python3 weather_cn.py --name 成都 --adm 四川
    python3 weather_cn.py --lat 30.55 --lon 104.10
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
    """获取城市信息（直接调用 GeoAPI，无本地缓存）"""
    city_info = fetch_city_coordinates(city_name, adm=adm)
    
    # Fallback: 区/县级名称导致 GeoAPI 返回 400 时，尝试向上级城市 fallback
    if not city_info:
        district_suffixes = ('区', '县', '镇', '乡', '街道', '开发区', '高新区', '新区')
        stripped = city_name
        for suffix in district_suffixes:
            if stripped.endswith(suffix):
                stripped = stripped[:-len(suffix)]
                break
        if stripped and stripped != city_name:
            city_info = fetch_city_coordinates(stripped, adm=adm)
        if not city_info and adm:
            city_info = fetch_city_coordinates(adm)
    
    if not city_info:
        print(f"查询城市信息失败")
        return None
    
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


def parse_args():
    """解析命令行参数，支持城市名或经纬度两种模式"""
    args = sys.argv[1:]
    
    # 模式1: 经纬度模式 --lat 30.55 --lon 104.10 --name 成都高新区
    lat = None
    lon = None
    name = "成都"
    adm = ""
    
    i = 0
    while i < len(args):
        if args[i] in ("--lat", "-lat") and i + 1 < len(args):
            lat = args[i + 1]
            i += 2
        elif args[i] in ("--lon", "-lon") and i + 1 < len(args):
            lon = args[i + 1]
            i += 2
        elif args[i] in ("--name", "-name") and i + 1 < len(args):
            name = args[i + 1]
            i += 2
        elif args[i] in ("--adm", "-adm") and i + 1 < len(args):
            adm = args[i + 1]
            i += 2
        else:
            # 剩余的作为位置参数（城市名+上级行政区）
            if not lat and not lon:
                if i == 0:
                    name = args[i]
                elif i == 1:
                    adm = args[i]
            i += 1
    
    return {"lat": lat, "lon": lon, "name": name, "adm": adm}

def main():
    """主函数"""
    args = parse_args()
    lat = args.get("lat")
    lon = args.get("lon")
    city_name = args.get("name")
    adm = args.get("adm", "")
    
    if lat and lon:
        # 模式1: 经纬度直查（和风天气 API 支持 location=lon,lat 格式）
        location_id = f"{lon},{lat}"
        latitude, longitude = lat, lon
    else:
        # 模式2: 城市名查询
        if not city_name:
            print("用法:\n"
                  " 按城市: python weather_cn.py --name 城市 [--adm 上级行政区]\n"
                  " 按坐标: python weather_cn.py --lat 30.55 --lon 104.10 [--name 位置名称]")
            sys.exit(1)
        
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
