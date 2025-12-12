#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow + OpenAI Agents SDK
最小多模态示例：单 Agent 图片问答
"""

# ===== 配置区（按需修改） =====
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_ID         = "Qwen/Qwen3-VL-235B-A22B-Thinking"   # 多模态 Qwen3 VL Thinking 版
API_KEY          = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"  # 这里填你的 SiliconFlow key

IMAGE_PATH       = "/home/zhangw/AML/AML_draft_impl/agents/image.png"
QUESTION         = "请说明这张图片的主要内容，并列出 3 个关键要素。"


# ===== 代码区（一般不用改） =====
import os
import base64
import mimetypes

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)


def to_data_url(path: str) -> str:
    """把本地图片转成 data URL（data:<mime>;base64,...）"""
    path = os.path.expanduser(path)
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# 关掉 OpenAI 官方的 tracing（否则会去找 OpenAI 平台的 key）
set_tracing_disabled(True)

# 用 SiliconFlow 的 OpenAI 兼容接口作为 client
client = AsyncOpenAI(
    base_url=SILICON_BASE_URL,
    api_key=API_KEY,
)

# 显式指定：这个 Agent 用的是 Chat Completions 形状 + 这个 client
model = OpenAIChatCompletionsModel(
    model=MODEL_ID,       # SiliconFlow 的多模态模型 ID
    openai_client=client, # 指向上面的 SiliconFlow client
)

# 定义一个多模态 Agent
agent = Agent(
    name="VisionAssistant",
    instructions="你是一个简洁的中文多模态助手，只用中文回答。",
    model=model,          # 注意：这里是 model 实例，而不是字符串
)


if __name__ == "__main__":
    # 1. 本地图片 → data URL
    img_data_url = to_data_url(IMAGE_PATH)

    # 2. 构造 Responses 风格 input（input_image + input_text）
    #    Agents 会把它转换成 chat.completions 的 messages，
    #    底层最后还是走 SiliconFlow 的 /v1/chat/completions。
    input_items = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": img_data_url,
                },
                {
                    "type": "input_text",
                    "text": QUESTION,
                },
            ],
        }
    ]

    # 3. 同步跑一轮
    result = Runner.run_sync(agent, input_items)
    print(result.final_output)
