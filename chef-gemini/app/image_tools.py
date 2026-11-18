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

"""Image generation tools for ChefGemini using gemini-3.1-flash-lite-image and GCS."""

import asyncio
import re
import uuid
from typing import Any

from google import genai
from google.adk.tools.tool_context import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-03-4bea0f6a557b"
BUCKET_NAME = "chef-gemini-recipes-4bea0f6a"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
IMAGE_LOCATION = "global"

_genai_client = None
_storage_client = None


def _get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=IMAGE_LOCATION,
        )
    return _genai_client


def _get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


async def generate_dish_image(
    dish_name: str,
    description: str = "",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """使用 Gemini 生成料理成品擬真照片，存入 Playground Artifacts 並上傳至 Cloud Storage 公開 Bucket。

    Args:
        dish_name: 料理名稱（例如 '嫩煎鮭魚佐藜麥時蔬' 或 '地中海彩椒雞胸肉'）。
        description: 料理的外觀特徵、盛盤風格或主要食材細節說明（可選）。
        tool_context: ADK 系統自動注入的上下文物件，用於調用 save_artifact。

    Returns:
        包含料理名稱、公開圖片網址 (image_url) 與 Artifact 檔名的字典。
    """
    client = _get_genai_client()
    prompt = (
        f"Professional studio food photography of {dish_name}. "
        f"{description}. "
        f"Appetizing presentation, delicious gourmet food styling, soft natural lighting, high resolution."
    )

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
    except Exception as e:
        return {"error": f"圖片生成失敗: {str(e)}"}

    image_bytes = None
    mime_type = "image/jpeg"

    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

    if not image_bytes:
        return {"error": f"未能成功為 '{dish_name}' 生成圖片資料"}

    safe_slug = re.sub(r"[^\w\-]", "_", dish_name.lower()).strip("_") or "dish"
    ext = "png" if "png" in mime_type else "jpg"
    artifact_filename = f"{safe_slug}.{ext}"

    # 1. 儲存為 Playground Artifact
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            res = tool_context.save_artifact(filename=artifact_filename, artifact=artifact_part)
            if asyncio.iscoroutine(res):
                await res
        except Exception as e:
            # 記錄但不中斷後續流程
            pass

    # 2. 上傳至 Cloud Storage 公開 Bucket
    try:
        storage_client = _get_storage_client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_name = f"recipes/{safe_slug}_{uuid.uuid4().hex[:8]}.{ext}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
    except Exception as e:
        return {"error": f"上傳至 Cloud Storage 失敗: {str(e)}"}

    return {
        "dish_name": dish_name,
        "image_url": public_url,
        "artifact_filename": artifact_filename,
    }
