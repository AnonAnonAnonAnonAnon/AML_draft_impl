#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM 统一封装示例：
provider = "doubao" / "silicon" / "uiui"
"""

# ===== 最快跑通：清掉 SOCKS/HTTP 代理环境变量（避免 httpx 报 socksio 缺失）=====
import os
for k in ("ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
    os.environ.pop(k, None)

from litellm import completion

# ===== 配置区 =====
DOUBAO_MODEL_ID = "volcengine/doubao-seed-1-6-251015"
DOUBAO_API_KEY  = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
SILICON_MODEL_ID = "openai/Qwen/Qwen3-VL-235B-A22B-Thinking"
SILICON_API_KEY  = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"

UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"     # 或 https://api1.uiuiapi.com/v1
UIUI_MODEL_ID = "openai/gpt-5.2"                # 也可试 "gpt-5.2"；不行就用控制台里的真实模型 ID
UIUI_API_KEY  = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"


def unified_chat(provider: str, user_msg: str) -> str:
    if provider == "doubao":
        model  = DOUBAO_MODEL_ID
        kwargs = {"api_key": DOUBAO_API_KEY}

    elif provider == "silicon":
        model  = SILICON_MODEL_ID
        kwargs = {"api_key": SILICON_API_KEY, "api_base": SILICON_BASE_URL}

    elif provider == "uiui":
        model  = UIUI_MODEL_ID
        kwargs = {"api_key": UIUI_API_KEY, "api_base": UIUI_BASE_URL}

    else:
        raise ValueError(f"未知 provider: {provider}")

    resp = completion(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=128,
        **kwargs,
    )
    return resp["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("---- uiui ----")
    print(unified_chat("uiui", "你好。请用一句话回复我。"))
    print("---- doubao ----")
    print(unified_chat("doubao", "简单介绍下你自己。"))
    print("---- silicon ----")
    print(unified_chat("silicon", "简单介绍下你自己。"))
