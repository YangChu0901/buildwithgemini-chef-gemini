# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from .a2ui_utils import a2ui_callback
from .firestore_tools import get_recipe_details, list_recipes, save_recipe
from .image_tools import generate_dish_image
from .maps_tools import find_nearby_places, geocode_address
from .nutrition_tools import calculate_nutrition_targets
from .public_api_tools import search_public_recipes
from .video_tools import generate_dish_video

MODEL = "gemini-3.8-flash"
SANDBOX_RESOURCE_NAME = (
    "projects/236665954902/locations/us-east1/reasoningEngines/2324621568304480256"
    "/sandboxEnvironments/5101016629168472064"
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "你是 ChefGemini（個人智慧主廚與營養管家）。"
        "【長期記憶與安全規範】你具備跨對話的長期記憶能力。每當使用者提及任何過敏原（如花生、海鮮、堅果、乳糖、麩質等）、飲食禁忌或食物不耐症時，必須格外嚴謹地記住，並在後續所有推薦食譜、規劃菜單與建議食材時嚴格避開該過敏原，以維護使用者的飲食安全。"
        "你可以協助使用者依據身體數值與目標精算熱量與營養素需求（TDEE / BMR / 蛋白質）、"
        "查詢內部資料庫食譜庫存、從全球公開食譜庫（TheMealDB）搜尋世界料理靈感、"
        "生成擬真高品質料理照片（Imagen/Gemini Image）或烹飪短片（Google Omni/gemini-omni-flash-preview）、"
        "將地址轉換為座標（Geocoding）、搜尋周邊超市與食材購買地點（Places API）、"
        "在安全的 Python 沙盒環境中執行代碼以進行精確科學計算、數據處理或食材配比模擬、"
        "查看料理步驟與營養成分，以及儲存或新增食譜至資料庫。請隨時以親切、專業的口吻提供實用的料理與生活建議。"
    ),
    workflow_description="Analyze the request, call relevant tools if needed, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        client_kwargs={"location": "global"},
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        list_recipes,
        get_recipe_details,
        save_recipe,
        calculate_nutrition_targets,
        search_public_recipes,
        geocode_address,
        find_nearby_places,
        generate_dish_image,
        generate_dish_video,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
