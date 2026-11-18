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

"""Public API tools for ChefGemini using TheMealDB API."""

import os
import requests
from typing import Any


def search_public_recipes(query: str) -> list[dict[str, Any]]:
    """從全球公開食譜庫 (TheMealDB) 搜尋料理靈感、食材與料理教學。

    Args:
        query: 料理或主要食材名稱（例如 'chicken', 'salmon', 'beef', 'pasta', 'soup' 等英文關鍵字）。

    Returns:
        包含料理名稱、料理菜系分類、食材清單、烹飪步驟及成品照片網址的清單列表。
    """
    api_key = os.environ.get("THEMEALDB_API_KEY", "1")
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php"

    try:
        response = requests.get(url, params={"s": query}, timeout=8)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return [{"error": f"公開食譜資料庫連線失敗: {str(e)}"}]

    meals = data.get("meals")
    if not meals:
        return [{"message": f"在公開食譜庫中未找到符合 '{query}' 的料理。"}]

    results = []
    # 取前 3 道最相關的料理
    for meal in meals[:3]:
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                measure_str = f" ({measure.strip()})" if measure and measure.strip() else ""
                ingredients.append(f"{ing.strip()}{measure_str}")

        instructions = meal.get("strInstructions", "")
        # 保留重點步驟摘要（避免 token 數過長）
        if len(instructions) > 500:
            instructions = instructions[:500] + "..."

        results.append({
            "name": meal.get("strMeal"),
            "category": meal.get("strCategory"),
            "cuisine": meal.get("strArea"),
            "image_url": meal.get("strMealThumb"),
            "ingredients": ingredients,
            "instructions": instructions,
        })

    return results
