#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow 最小测试：
直接用 openai 官方 SDK 调 /v1/chat/completions 做一次中文问答
"""

# ===== 配置区（按需修改） =====
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
# MODEL_ID         = "Qwen/QwQ-32B"   # 或文档里列出的任意一个模型
MODEL_ID         = "Qwen/Qwen3-VL-235B-A22B-Thinking"   # 或文档里列出的任意一个模型
API_KEY          = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"  # 直接写你的 key

# ===== 代码区（一般不用改） =====
from openai import OpenAI


# 初始化 SiliconFlow 客户端（OpenAI 兼容协议）
client = OpenAI(
    base_url=SILICON_BASE_URL,
    api_key=API_KEY,
)


def main():
    # 最简单的一轮对话
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user", "content": "用一句话介绍一下你自己，并说明你是通过 SiliconFlow 被调用的。"},
        ],
        max_tokens=512,
        temperature=0.7,
        # 下面这些都可以先不设，默认就行：
        # stream=False,
        # enable_thinking=False,
    )

    msg = resp.choices[0].message

    print("----- answer -----")
    print(msg.content)

    # 如果想看 token 用量
    if getattr(resp, "usage", None):
        print("----- usage -----")
        print(resp.usage)


if __name__ == "__main__":
    main()
