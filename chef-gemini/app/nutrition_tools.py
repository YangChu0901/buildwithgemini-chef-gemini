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

"""Nutrition and TDEE calculator tool for ChefGemini."""

from typing import Any


def calculate_nutrition_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str = "moderate",
    goal: str = "weight_loss",
) -> dict[str, Any]:
    """精算使用者的基礎代謝率 (BMR)、每日總能量消耗 (TDEE) 及目標巨量營養素比例。

    Args:
        weight_kg: 體重（公斤 kg）。
        height_cm: 身高（公分 cm）。
        age: 年齡（歲）。
        gender: 性別，'male' / '男' 或 'female' / '女'。
        activity_level: 活動程度：
            - 'sedentary' / '久坐': 幾乎不運動或辦公室久坐
            - 'light' / '輕度': 每週輕度運動 1-3 天
            - 'moderate' / '中度': 每週中度運動 3-5 天（預設）
            - 'active' / '高活動': 每週運動 6-7 天
        goal: 健康目標：
            - 'weight_loss' / '減脂': 熱量赤字，建議高蛋白
            - 'muscle_gain' / '增肌': 適度熱量盈餘，充足蛋白質與碳水
            - 'maintenance' / '維持': 熱量平衡
            - 'low_carb' / '低醣': 限制碳水化合物比例

    Returns:
        包含 BMR、TDEE、目標每日熱量 (target_calories)、三餐建議熱量上限 (per_meal_target_calories)，
        以及蛋白質 (protein_g)、碳水化合物 (carbs_g)、脂肪 (fat_g) 建議克數的字典。
    """
    # 1. 計算 BMR (Mifflin-St Jeor 公式)
    is_male = gender.lower() in ["male", "m", "男", "男性"]
    if is_male:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # 2. 活動係數
    act_map = {
        "sedentary": 1.2,
        "久坐": 1.2,
        "light": 1.375,
        "輕度": 1.375,
        "moderate": 1.55,
        "中度": 1.55,
        "active": 1.725,
        "高活動": 1.725,
    }
    multiplier = act_map.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier

    # 3. 依目標調整每日總熱量與巨量營養素
    goal_norm = goal.lower()
    if any(k in goal_norm for k in ["loss", "減", "瘦"]):
        # 減脂：約 20% 赤字
        target_calories = round(tdee * 0.8)
        # 高蛋白以保護肌肉：每公斤體重 2.0g
        protein_g = round(weight_kg * 2.0, 1)
        # 脂肪約佔總熱量 25% (1g 脂肪 = 9 kcal)
        fat_g = round((target_calories * 0.25) / 9, 1)
        # 剩餘熱量分配給碳水化合物 (1g 碳水 = 4 kcal, 1g 蛋白質 = 4 kcal)
        remaining_kcal = target_calories - (protein_g * 4) - (fat_g * 9)
        carbs_g = round(max(30.0, remaining_kcal / 4), 1)
        goal_desc = "減脂目標（熱量赤字 20%，提高蛋白質以保護肌肉）"
    elif any(k in goal_norm for k in ["muscle", "gain", "增肌", "壯"]):
        # 增肌：約 10% 熱量盈餘
        target_calories = round(tdee * 1.1)
        protein_g = round(weight_kg * 1.8, 1)
        fat_g = round((target_calories * 0.25) / 9, 1)
        remaining_kcal = target_calories - (protein_g * 4) - (fat_g * 9)
        carbs_g = round(max(50.0, remaining_kcal / 4), 1)
        goal_desc = "增肌目標（適度熱量盈餘 10%，充足碳水為訓練供能）"
    elif any(k in goal_norm for k in ["low_carb", "低醣", "生酮"]):
        # 低醣：碳水控制在 60g 內
        target_calories = round(tdee * 0.85)
        carbs_g = 60.0
        protein_g = round(weight_kg * 1.8, 1)
        remaining_kcal = target_calories - (carbs_g * 4) - (protein_g * 4)
        fat_g = round(max(30.0, remaining_kcal / 9), 1)
        goal_desc = "低醣目標（嚴格控制碳水化合物，適度增加優質脂肪）"
    else:
        # 維持體態
        target_calories = round(tdee)
        protein_g = round(weight_kg * 1.6, 1)
        fat_g = round((target_calories * 0.28) / 9, 1)
        remaining_kcal = target_calories - (protein_g * 4) - (fat_g * 9)
        carbs_g = round(max(50.0, remaining_kcal / 4), 1)
        goal_desc = "維持目前體態（熱量收支平衡）"

    # 單餐建議熱量（假設每日三餐，每餐約佔 30~35%）
    per_meal_target = round(target_calories / 3)

    return {
        "bmr_kcal": round(bmr),
        "tdee_kcal": round(tdee),
        "target_daily_calories_kcal": target_calories,
        "per_meal_target_calories_kcal": per_meal_target,
        "protein_target_g": protein_g,
        "carbs_target_g": carbs_g,
        "fat_target_g": fat_g,
        "goal_description": goal_desc,
    }
