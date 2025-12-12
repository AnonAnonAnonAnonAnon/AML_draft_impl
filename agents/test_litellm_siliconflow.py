#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM + SiliconFlow 最小测试：
用 Qwen3-VL-235B-A22B-Thinking 做一次中文问答（只文本）
"""

# ===== 配置区（按需修改） =====
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
# LiteLLM 要求 openai/ 前缀来走 OpenAI-compatible 模式
SILICON_MODEL_ID = "openai/Qwen/Qwen3-VL-235B-A22B-Thinking"
SILICON_API_KEY  = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"


# ===== 代码区（一般不用改） =====
from litellm import completion


def chat_with_silicon(user_msg: str) -> str:
    resp = completion(
        model=SILICON_MODEL_ID,
        messages=[
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user",   "content": user_msg},
        ],
        api_key=SILICON_API_KEY,
        api_base=SILICON_BASE_URL,  # 指向 SiliconFlow 的 /v1
        temperature=0.3,
        max_tokens=512,
    )
    return resp["choices"][0]["message"]["content"]


if __name__ == "__main__":
    ans = chat_with_silicon("用一句话介绍一下你自己，并说明你是通过 LiteLLM + SiliconFlow 被调用的。")
    print("----- answer (siliconflow) -----")
    print(ans)
