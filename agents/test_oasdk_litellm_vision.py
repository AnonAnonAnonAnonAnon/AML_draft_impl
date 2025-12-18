#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM as backend + OpenAI Agents SDK
- 文本/视觉都在一个脚本里跑
"""

# ===== 配置区（按需修改） =====
PROVIDER   = "uiui"  # "uiui" / "doubao" / "silicon"
MODE       = "vision"   # "text" / "vision"
USER_PROMPT = "你好。请用一句话回复我。"

IMAGE_PATH = "/home/liwenbo/projects/AML/AML_draft_impl/agents/image.png"
QUESTION   = "请说明这张图片的主要内容，并列出 3 个关键要素。"

# --- UIUI ---
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
UIUI_MODEL_ID = "openai/gpt-5.2"
UIUI_API_KEY  = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"

# --- 豆包（Volcengine）---
DOUBAO_MODEL_ID = "volcengine/doubao-seed-1-6-251015"
DOUBAO_API_KEY  = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

# --- 硅基流动（SiliconFlow）---
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
SILICON_MODEL_ID = "openai/Qwen/Qwen3-VL-235B-A22B-Thinking"
SILICON_API_KEY  = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"

# ===== 代码区（一般不用改） =====
import os

# 1) 最稳：import agents 之前就全局禁用 tracing
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

# 2) 最稳：强制关闭 LiteLLM payload 打印（否则会把 base64 data-url 刷屏）
os.environ["LITELLM_PRINT_STANDARD_LOGGING_PAYLOAD"] = "false"

import base64
import mimetypes
import logging

logging.getLogger("litellm").setLevel(logging.WARNING)

import litellm
litellm.set_verbose = False

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel


def to_data_url(path: str) -> str:
    path = os.path.expanduser(path)
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def make_litellm_model(provider: str) -> LitellmModel:
    if provider == "uiui":
        return LitellmModel(model=UIUI_MODEL_ID, base_url=UIUI_BASE_URL, api_key=UIUI_API_KEY)
    if provider == "doubao":
        return LitellmModel(model=DOUBAO_MODEL_ID, api_key=DOUBAO_API_KEY)
    if provider == "silicon":
        return LitellmModel(model=SILICON_MODEL_ID, base_url=SILICON_BASE_URL, api_key=SILICON_API_KEY)
    raise ValueError(f"未知 PROVIDER: {provider}")


def main():
    agent = Agent(
        name="Assistant",
        instructions="你是一个简洁的中文助手，只用中文回答。",
        model=make_litellm_model(PROVIDER),
    )

    if MODE == "text":
        result = Runner.run_sync(agent, USER_PROMPT)
        print(result.final_output)
        return

    img_data_url = to_data_url(IMAGE_PATH)
    input_items = [{
        "role": "user",
        "content": [
            {"type": "input_image", "image_url": img_data_url},
            {"type": "input_text",  "text": QUESTION},
        ],
    }]

    result = Runner.run_sync(agent, input_items)
    print(result.final_output)


if __name__ == "__main__":
    main()
