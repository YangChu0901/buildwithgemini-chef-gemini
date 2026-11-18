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

"""Video generation tools for ChefGemini using gemini-omni-flash-preview and Cloud Storage."""

import asyncio
import base64
import re
from typing import Any
import uuid

from google import genai
from google.adk.tools.tool_context import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-03-4bea0f6a557b"
BUCKET_NAME = "chef-gemini-recipes-4bea0f6a"
VIDEO_MODEL = "gemini-omni-flash-preview"
VIDEO_LOCATION = "global"

_genai_client = None
_storage_client = None


def _get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=VIDEO_LOCATION,
        )
    return _genai_client


def _get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


async def generate_dish_video(
    dish_name: str,
    description: str = "",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """使用 Google Omni 模型 (gemini-omni-flash-preview) 生成料理或烹飪過程短片，存入 Playground Artifacts 並上傳至 Cloud Storage 公開 Bucket。

    Args:
        dish_name: 料理或食材名稱（例如 '香煎嫩鮭魚'、'義式香草烤雞' 或 '地中海彩椒牛肉'）。
        description: 烹飪動作、火候、擺盤或鏡頭運鏡說明（例如 '平底鍋熱油滋滋作響'、'主廚淋上初榨橄欖油與黑胡椒'）。
        tool_context: ADK 系統自動注入的上下文物件，用於調用 save_artifact。

    Returns:
        包含料理名稱、公開影片網址 (video_url) 與 Artifact 檔名的字典。
    """
    client = _get_genai_client()
    prompt = (
        f"A cinematic culinary short video showing {dish_name}. "
        f"{description}. "
        f"Appetizing gourmet food preparation, sizzling textures, vibrant natural lighting, smooth 4k camera movement."
    )

    try:
        interaction = client.interactions.create(
            model=VIDEO_MODEL,
            input=prompt,
        )
    except Exception as e:
        return {"error": f"影片生成失敗: {str(e)}"}

    video_bytes = None
    mime_type = "video/mp4"

    if getattr(interaction, "output_video", None):
        ov = interaction.output_video
        if getattr(ov, "mime_type", None):
            mime_type = str(ov.mime_type)
        if getattr(ov, "data", None):
            if isinstance(ov.data, str):
                video_bytes = base64.b64decode(ov.data)
            elif isinstance(ov.data, bytes):
                video_bytes = ov.data
        elif getattr(ov, "uri", None):
            # If returned as a URI, fetch bytes in memory without saving to local file
            import httpx
            try:
                resp = httpx.get(ov.uri, timeout=60.0)
                resp.raise_for_status()
                video_bytes = resp.content
            except Exception:
                pass

    # Fallback: check interaction.steps if output_video was not directly populated
    if not video_bytes and getattr(interaction, "steps", None):
        for step in reversed(interaction.steps):
            if getattr(step, "type", None) == "model_output":
                for item in getattr(step, "content", []) or []:
                    if getattr(item, "type", None) == "video" and getattr(item, "data", None):
                        data_val = getattr(item, "data")
                        if isinstance(data_val, str):
                            video_bytes = base64.b64decode(data_val)
                        elif isinstance(data_val, bytes):
                            video_bytes = data_val
                        if getattr(item, "mime_type", None):
                            mime_type = str(item.mime_type)
                        break
                if video_bytes:
                    break

    if not video_bytes:
        return {"error": f"未能成功為 '{dish_name}' 取得生成影片資料"}

    safe_slug = re.sub(r"[^\w\-]", "_", dish_name.lower()).strip("_") or "video"
    ext = "mp4"
    if "webm" in mime_type:
        ext = "webm"
    artifact_filename = f"{safe_slug}.{ext}"

    # 1. 儲存至 Playground Artifacts (tool_context.save_artifact)
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            res = tool_context.save_artifact(filename=artifact_filename, artifact=artifact_part)
            if asyncio.iscoroutine(res):
                await res
        except Exception:
            # 記錄但不中斷後續上傳流程
            pass

    # 2. 上傳至 Cloud Storage 公開 Bucket 並返回公開 https URL
    try:
        storage_client = _get_storage_client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_name = f"videos/{safe_slug}_{uuid.uuid4().hex[:8]}.{ext}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(video_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
    except Exception as e:
        return {"error": f"上傳至 Cloud Storage 失敗: {str(e)}"}

    return {
        "dish_name": dish_name,
        "video_url": public_url,
        "artifact_filename": artifact_filename,
    }
