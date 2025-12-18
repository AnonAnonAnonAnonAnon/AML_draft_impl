#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIUI + OpenAI Agent SDK 最小测试（chat.completions）
"""

# ===== 配置区（按需修改） =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"   # 或 https://api1.uiuiapi.com/v1
MODEL_ID      = "gpt-5.2"                    # 若报 model not found，请用 UIUI 控制台显示的真实模型 ID
API_KEY       = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"    # 填你的 UIUI Key

# ===== 代码区（一般不用改） =====
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 用 UIUI 的 OpenAI 兼容接口替换默认 client
client = AsyncOpenAI(
    base_url=UIUI_BASE_URL,
    api_key=API_KEY,
)

# 告诉 Agents：用 chat.completions，而不是 Responses API
set_default_openai_api("chat_completions")

# 默认所有 Agent 都走这个 UIUI client
set_default_openai_client(client)

# 关掉 tracing（否则可能会去找 OpenAI 的 key / tracing 配置）
set_tracing_disabled(True)

# 定义一个最小 Agent
agent = Agent(
    name="Assistant",
    instructions="你是一个简洁的中文助手，只用中文回答。",
    model=MODEL_ID,
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "你好。用一句话介绍你自己。")
    print(result.final_output)
