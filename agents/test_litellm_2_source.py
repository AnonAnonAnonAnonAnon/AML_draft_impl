#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM 统一封装示例：
provider = "doubao" / "silicon"
"""

from litellm import completion

# ===== 配置区 =====
DOUBAO_MODEL_ID = "volcengine/doubao-seed-1-6-251015"
DOUBAO_API_KEY  = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
SILICON_MODEL_ID = "openai/Qwen/Qwen3-VL-235B-A22B-Thinking"
SILICON_API_KEY  = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"


def unified_chat(provider: str, user_msg: str) -> str:
    if provider == "doubao":
        model   = DOUBAO_MODEL_ID
        kwargs  = {"api_key": DOUBAO_API_KEY}
    elif provider == "silicon":
        model   = SILICON_MODEL_ID
        kwargs  = {"api_key": SILICON_API_KEY, "api_base": SILICON_BASE_URL}
    else:
        raise ValueError(f"未知 provider: {provider}")

    resp = completion(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=512,
        **kwargs,
    )
    return resp["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("---- doubao ----")
    print(unified_chat("doubao", "简单介绍下你自己。"))

    print("---- silicon ----")
    print(unified_chat("silicon", "简单介绍下你自己。"))
