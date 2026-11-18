# My agent: ChefGemini (個人智慧主廚與營養管家)
One-liner: A conversational agent that helps home cooks plan meals, manage pantry ingredients, and cook personalized healthy dishes with a catalog of curated recipes and nutrition data.

Tool coverage:
- Memory: 使用者的飲食偏好、過敏原（如花生、麩質）、討厭的食材、家庭成員人數、健康目標（減脂、增肌、低醣）。
- Tools: 食譜資料庫查詢（依現有食材與熱量篩選）、冰箱庫存增刪查改（Pantry Manager）、營養成分計算。
- Catalog/UI: 食譜清單與菜色詳情卡片（烹調時間、難易度、食材清單、營養標籤）、每週餐單表格。
- Image gen: 根據生成的客製化食譜即時生成擺盤完成圖與料理示意視覺。
- Sandbox: 根據使用者體重與目標熱量，執行 Python 計算每日巨量營養素比例（碳水/蛋白質/脂肪）以及根據用餐人數自動縮放食材克數。

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code Sandbox 營養與份量精確計算、Firestore 存放用戶專屬食譜與庫存、Vertex AI RAG 檢索專業營養指南
