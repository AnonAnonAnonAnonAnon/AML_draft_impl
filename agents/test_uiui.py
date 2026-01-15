#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIUIAPI 最小测试：
用 OpenAI 官方 Python SDK（OpenAI 兼容协议）调用 /v1/chat/completions 做一次“你好”问答
依赖：pip install -U openai
"""

# ===== 配置区（按需修改） =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"   # 或 "https://api1.uiuiapi.com/v1"
MODEL_ID      = "gpt-5.2"                     # 如报 model not found，请在 UIUI 控制台复制真实模型 ID
# API_KEY       = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf" # 常规key
API_KEY       = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5" # codex通道key
# API_KEY       = "sk-dBZBwnWoziBr4omEIZgPQX7B6aZzjFpCJd5DK3jqa7hn9sml" # codex通道key 0115新



# ===== 代码区（一般不用改） =====
from openai import OpenAI
import httpx

client = OpenAI(
    base_url=UIUI_BASE_URL,
    api_key=API_KEY,
)

# client = OpenAI(
#     base_url=UIUI_BASE_URL,
#     api_key=API_KEY,
#     http_client=httpx.Client(trust_env=False),  # 忽略 ALL_PROXY 等环境变量
# )

def main():
    # （可选）先看一眼可用模型列表（若 UIUI 开了 /v1/models）
    # try:
    #     models = client.models.list()
    #     print("----- models (head) -----")
    #     print([m.id for m in models.data[:20]])
    # except Exception as e:
    #     print("----- models list failed (ignore) -----")
    #     print(e)

    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user", "content": "你好。请用一句话回复我。"},
        ],
        temperature=0.2,
        max_tokens=128,
    )

    print("----- answer -----")
    print(resp.choices[0].message.content)

    if getattr(resp, "usage", None):
        print("----- usage -----")
        print(resp.usage)

if __name__ == "__main__":
    main()
