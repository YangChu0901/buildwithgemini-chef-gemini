# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Maps Geocoding and Places API (New) tools for ChefGemini."""

import os
from typing import Any
from dotenv import load_dotenv
import requests

load_dotenv()


def _get_api_key() -> str:
    """從環境變數讀取 Google Maps API 金鑰，不寫死於原始碼中。"""
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("找不到 GOOGLE_MAPS_API_KEY 環境變數，請確認已在 .env 中設定。")
    return key


def geocode_address(address: str) -> dict[str, Any]:
    """使用 Google Geocoding API 將地址或地標轉換為經緯度座標。

    Args:
        address: 欲查詢的地址或地標名稱（例如 '1600 Amphitheatre Parkway, Mountain View, CA' 或 '台北車站'）。

    Returns:
        包含格式化地址 (address) 與經緯度座標 (location: latitude, longitude) 的字典。
    """
    api_key = _get_api_key()
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"error": f"Geocoding API 請求失敗: {str(e)}"}

    if data.get("status") != "OK" or not data.get("results"):
        return {"error": f"無法解析地址 '{address}'，狀態碼: {data.get('status')}"}

    first_result = data["results"][0]
    loc = first_result["geometry"]["location"]
    return {
        "address": first_result.get("formatted_address"),
        "location": {
            "latitude": loc["lat"],
            "longitude": loc["lng"],
        },
    }


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "supermarket",
    radius_meters: float = 3000.0,
) -> list[dict[str, Any]]:
    """使用 Places API (New) 搜尋指定座標周邊的特定場所（例如超市、生鮮超市、餐廳等）。

    Args:
        latitude: 中心緯度（例如 37.4220）。
        longitude: 中心經度（例如 -122.0841）。
        place_type: 場所類型，例如 'supermarket'（超市）、'grocery_store'（雜貨生鮮）、'restaurant'（餐廳）。預設為 'supermarket'。
        radius_meters: 搜尋半徑範圍（公尺），預設為 3000 公尺（最大可至 50000）。

    Returns:
        符合條件的周邊地點列表，每個地點包含名稱 (name)、地址 (address) 與座標 (location)。
    """
    api_key = _get_api_key()
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
          "circle": {
            "center": {
              "latitude": latitude,
              "longitude": longitude,
            },
            "radius": float(radius_meters),
          }
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return [{"error": f"Places API (New) 請求失敗: {str(e)}"}]

    places = data.get("places", [])
    if not places:
        return [{"message": f"在經緯度 ({latitude}, {longitude}) 方圓 {radius_meters} 公尺內未找到 {place_type} 相關地點。"}]

    results = []
    for place in places:
        display_name = place.get("displayName", {}).get("text", "")
        results.append({
            "name": display_name,
            "address": place.get("formattedAddress", ""),
            "location": place.get("location", {}),
        })

    return results
