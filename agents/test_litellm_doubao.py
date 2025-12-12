#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM + 豆包(Volcengine) 最小测试：
用 doubao-seed-1-6-251015 做一次中文问答
"""

# ===== 配置区（按需修改） =====
DOUBAO_MODEL_ID = "volcengine/doubao-seed-1-6-251015"  # 注意前缀 volcengine/
DOUBAO_API_KEY  = "70f0d563-91a5-4704-a00e-f00cf3a9c864"              # 和你之前豆包脚本里的 key 一样


# ===== 代码区（一般不用改） =====
from litellm import completion


def chat_with_doubao(user_msg: str) -> str:
    resp = completion(
        model=DOUBAO_MODEL_ID,
        messages=[
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user",   "content": user_msg},
        ],
        api_key=DOUBAO_API_KEY,  # 不用环境变量，直接传参数
        temperature=0.3,
        max_tokens=512,
    )
    # LiteLLM 返回的是 OpenAI 兼容格式
    return resp["choices"][0]["message"]["content"]


if __name__ == "__main__":
    ans = chat_with_doubao("用一句话介绍一下你自己，并说明你是通过 LiteLLM + 豆包 被调用的。")
    print("----- answer (doubao) -----")
    print(ans)
