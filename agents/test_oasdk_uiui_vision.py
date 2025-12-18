#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIUI + OpenAI Agents SDK + 视觉问答（最小版，chat.completions）
依赖：
  pip install -U openai openai-agents
"""

# ===== 配置区（按需修改） =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"      # 或 "https://api1.uiuiapi.com/v1"
MODEL_ID      = "gpt-5.2"                        # 以 UIUI 控制台/模型列表为准
API_KEY       = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"

IMAGE_PATH    = "/home/liwenbo/projects/AML/AML_draft_impl/agents/image.png"
QUESTION      = "请说明这张图片的主要内容，并列出 3 个关键要素。"


# ===== 代码区（一般不用改） =====
import os
import base64
import mimetypes

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)


def to_data_url(path: str) -> str:
    """本地图片 -> data:<mime>;base64,..."""
    path = os.path.expanduser(path)
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# 用 UIUI 的 OpenAI 兼容接口作为全局 client
client = AsyncOpenAI(
    base_url=UIUI_BASE_URL,
    api_key=API_KEY,
)

# 告诉 Agents：底层用 chat.completions
set_default_openai_api("chat_completions")
set_default_openai_client(client)

# 关 tracing（否则可能会去找 OpenAI tracing 配置）
set_tracing_disabled(True)

# 最小 Agent
agent = Agent(
    name="VisionAssistant",
    instructions="你是一个简洁的中文多模态助手，只用中文回答。",
    model=MODEL_ID,
)

if __name__ == "__main__":
    img_data_url = to_data_url(IMAGE_PATH)

    # Responses 风格输入（Agents 会转成 chat.completions）
    input_items = [{
        "role": "user",
        "content": [
            {"type": "input_image", "image_url": img_data_url},
            {"type": "input_text", "text": QUESTION},
        ],
    }]

    result = Runner.run_sync(agent, input_items)
    print(result.final_output)
