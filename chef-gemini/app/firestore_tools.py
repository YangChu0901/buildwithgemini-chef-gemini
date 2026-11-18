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

"""Firestore database tools for ChefGemini recipes catalog."""

from typing import Any, Optional
from google.cloud import firestore

# Hardcode project ID as string constant to avoid project number resolution on Agent Platform
PROJECT_ID = "qwiklabs-gcp-03-4bea0f6a557b"

_db_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client instance."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def list_recipes(
    category: Optional[str] = None,
    max_calories: Optional[int] = None,
    tag: Optional[str] = None,
) -> list[dict[str, Any]]:
    """查詢食譜清單，可依分類、最高熱量限制或特定飲食標籤（例如高蛋白、無麩質、低醣）篩選。

    Args:
        category: 食譜分類（如「海鮮料理」、「減脂輕食」、「蔬食高蛋白」、「健康早餐」、「增肌增能」），可為空。
        max_calories: 最高熱量上限（大卡 kcal），可為空。
        tag: 飲食特性標籤（如「高蛋白」、「低醣」、「無麩質」、「純素」），可為空。

    Returns:
        符合條件的食譜清單列表，每道食譜包含 id、title、category、calories、protein_g 等基本摘要資訊。
    """
    db = get_firestore_client()
    recipes_ref = db.collection("recipes")
    docs = recipes_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # 篩選條件
        if category and category.lower() not in data.get("category", "").lower():
            continue
        if max_calories is not None and data.get("calories", 0) > max_calories:
            continue
        if tag:
            tags = [t.lower() for t in data.get("tags", [])]
            if tag.lower() not in tags:
                continue

        results.append({
            "id": data["id"],
            "title": data.get("title", ""),
            "category": data.get("category", ""),
            "prep_time_minutes": data.get("prep_time_minutes", 0),
            "calories": data.get("calories", 0),
            "protein_g": data.get("protein_g", 0),
            "tags": data.get("tags", []),
        })

    return results


def get_recipe_details(recipe_id: str) -> dict[str, Any]:
    """取得指定食譜的完整詳細內容，包含詳細食材清單、料理步驟與營養素。

    Args:
        recipe_id: 食譜的唯一識別碼（例如 'grilled-salmon-quinoa'、'chicken-avocado-salad'）。

    Returns:
        包含完整食材配方、料理步驟與熱量營養成分的字典；若無此食譜則回傳錯誤提示。
    """
    db = get_firestore_client()
    doc_ref = db.collection("recipes").document(recipe_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"找不到識別碼為 '{recipe_id}' 的食譜。"}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_recipe(
    recipe_id: str,
    title: str,
    category: str,
    prep_time_minutes: int,
    calories: int,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    ingredients: list[str],
    instructions: list[str],
    tags: Optional[list[str]] = None,
) -> str:
    """新增或儲存自訂食譜至雲端資料庫。

    Args:
        recipe_id: 食譜的英文唯一識別碼（如 'greek-lemon-chicken'）。
        title: 食譜名稱（如「希臘檸檬烤雞腿」）。
        category: 料理分類（如「主餐」、「減脂輕食」）。
        prep_time_minutes: 準備與烹飪總時間（分鐘）。
        calories: 單人份總熱量（kcal）。
        protein_g: 蛋白質含量（克）。
        carbs_g: 碳水化合物含量（克）。
        fat_g: 脂肪含量（克）。
        ingredients: 食材清單（例如 ['去骨雞腿排 200g', '檸檬汁 2大匙', '蒜泥 1茶匙']）。
        instructions: 烹調步驟步驟列表（例如 ['雞腿排以檸檬汁與鹽醃製20分鐘', '氣炸鍋180度烤15分鐘']）。
        tags: 標籤清單（可選，如 ['低醣', '高蛋白']）。

    Returns:
        操作成功提示訊息。
    """
    db = get_firestore_client()
    data = {
        "id": recipe_id,
        "title": title,
        "category": category,
        "prep_time_minutes": prep_time_minutes,
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "ingredients": ingredients,
        "instructions": instructions,
        "tags": tags or [],
    }
    db.collection("recipes").document(recipe_id).set(data)
    return f"成功儲存食譜「{title}」（ID: {recipe_id}）至資料庫！"
