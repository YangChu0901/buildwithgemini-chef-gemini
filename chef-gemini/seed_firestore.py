#!/usr/bin/env python3
"""Seed Firestore recipes collection for ChefGemini."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-4bea0f6a557b"

SAMPLE_RECIPES = [
    {
        "id": "grilled-salmon-quinoa",
        "title": "香煎鮭魚佐藜麥時蔬",
        "category": "海鮮料理",
        "prep_time_minutes": 20,
        "calories": 480,
        "protein_g": 38.0,
        "carbs_g": 32.0,
        "fat_g": 22.0,
        "ingredients": [
            "鮭魚排 150g",
            "熟藜麥 100g",
            "花椰菜 80g",
            "小番茄 4顆",
            "特級初榨橄欖油 1茶匙",
            "黑胡椒與海鹽 適量",
        ],
        "instructions": [
            "鮭魚兩面撒上少許黑胡椒與海鹽醃製5分鐘。",
            "熱平底鍋倒入少許橄欖油，皮朝下中小火煎4分鐘至酥脆，翻面續煎3分鐘至熟透。",
            "花椰菜與小番茄燙熟瀝乾備用。",
            "在盤中盛入熱藜麥飯，擺上香煎鮭魚與時蔬即可享用。",
        ],
        "tags": ["高蛋白", "Omega-3", "無麩質", "減脂"],
    },
    {
        "id": "chicken-avocado-salad",
        "title": "低脂嫩煎雞胸酪梨沙拉",
        "category": "減脂輕食",
        "prep_time_minutes": 15,
        "calories": 360,
        "protein_g": 42.0,
        "carbs_g": 12.0,
        "fat_g": 14.0,
        "ingredients": [
            "去皮雞胸肉 180g",
            "熟酪梨 半顆切片",
            "綜合生菜 100g",
            "檸檬汁 1茶匙",
            "巴薩米克醋 1茶匙",
            "蒜粉與黑胡椒 適量",
        ],
        "instructions": [
            "雞胸肉劃斜刀，以蒜粉、黑胡椒及少許鹽抓醃。",
            "平底鍋噴薄油，中火將雞胸肉兩面煎至微焦全熟，起鍋靜置2分鐘後切片。",
            "將綜合生菜洗淨甩乾鋪底，放上切片雞胸肉與酪梨片。",
            "淋上檸檬汁與巴薩米克醋即可享用。",
        ],
        "tags": ["低醣", "生酮友善", "高蛋白", "減脂"],
    },
    {
        "id": "tofu-veggie-stir-fry",
        "title": "日式照燒彩椒嫩豆腐",
        "category": "蔬食高蛋白",
        "prep_time_minutes": 15,
        "calories": 310,
        "protein_g": 22.0,
        "carbs_g": 26.0,
        "fat_g": 12.0,
        "ingredients": [
            "板豆腐 1塊(約200g)",
            "紅黃彩椒 各半顆切塊",
            "毛豆仁 50g",
            "低鈉醬油 1大匙",
            "味醂 1茶匙",
            "白芝麻 少許",
        ],
        "instructions": [
            "板豆腐以廚房紙巾吸乾水分，切成2公分厚方塊。",
            "少油熱鍋，將豆腐塊各面煎至金黃微酥盛出備用。",
            "原鍋拌炒彩椒與毛豆仁至斷生，倒回煎好的豆腐。",
            "淋上低鈉醬油與味醂快速翻炒收汁，起鍋撒上白芝麻。",
        ],
        "tags": ["純素", "高纖", "植物性蛋白", "低卡"],
    },
    {
        "id": "berry-greek-yogurt-bowl",
        "title": "高蛋白莓果奇亞籽優格碗",
        "category": "健康早餐",
        "prep_time_minutes": 5,
        "calories": 280,
        "protein_g": 24.0,
        "carbs_g": 30.0,
        "fat_g": 6.0,
        "ingredients": [
            "無糖希臘優格 200g",
            "冷凍綜合莓果 60g",
            "奇亞籽 1大匙",
            "無調味杏仁碎 10g",
            "純蜂蜜 1茶匙",
        ],
        "instructions": [
            "將無糖希臘優格盛入大碗中作為基底。",
            "鋪上綜合莓果與奇亞籽。",
            "灑上烘烤杏仁碎增添酥脆口感。",
            "依個人喜好淋上少許純蜂蜜調味即可食用。",
        ],
        "tags": ["免開火", "高蛋白", "益生菌", "快速早餐"],
    },
    {
        "id": "beef-sweet-potato-plate",
        "title": "黑胡椒炙烤牛里肌佐烤地瓜",
        "category": "增肌增能",
        "prep_time_minutes": 25,
        "calories": 520,
        "protein_g": 45.0,
        "carbs_g": 48.0,
        "fat_g": 16.0,
        "ingredients": [
            "牛里肌肉 180g",
            "紅心地瓜 1條(約150g)",
            "綠蘆筍 6根",
            "蒜瓣 2顆",
            "黑胡椒粒與海鹽 適量",
        ],
        "instructions": [
            "地瓜洗淨切滾刀塊，微波或烤箱烤至鬆軟透心。",
            "牛里肌回溫，抹上海鹽與現磨黑胡椒。",
            "鑄鐵鍋高火熱鍋，將牛排每面煎約1.5分鐘鎖住肉汁，放入蒜瓣提味，起鍋靜置5分鐘切片。",
            "原鍋快速乾煎蘆筍2分鐘，與烤地瓜、炙烤牛里肌一同盛盤。",
        ],
        "tags": ["增肌", "優質碳水", "高蛋白", "低GI"],
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("recipes")

    print(f"Seeding recipes collection in project '{PROJECT_ID}'...")
    for item in SAMPLE_RECIPES:
        doc_ref = collection_ref.document(item["id"])
        doc_ref.set(item)
        print(f"  ✓ Seeded: {item['id']} - {item['title']}")

    print(f"Successfully seeded {len(SAMPLE_RECIPES)} recipes into Firestore!")


if __name__ == "__main__":
    seed_database()
