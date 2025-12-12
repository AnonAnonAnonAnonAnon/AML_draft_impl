#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow + OpenAI Agents SDK
最小可运行示例：单 Agent 文本对话
"""

# ===== 配置区（按需修改） =====
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_ID         = "Qwen/Qwen3-VL-235B-A22B-Thinking"   # 多模态 + Thinking 版
API_KEY          = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"           # 直接写 SiliconFlow 的 sk- 开头密钥


# ===== 代码区（一般不用改） =====
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)

# 关掉 OpenAI 官方的 tracing（否则会去找 OpenAI 平台的 key）
set_tracing_disabled(True)

# 用 SiliconFlow 的 OpenAI 兼容接口作为 client
client = AsyncOpenAI(
    base_url=SILICON_BASE_URL,
    api_key=API_KEY,
)

# 显式指定：这个 Agent 用的是「Chat Completions 形状」+ 这个 client
model = OpenAIChatCompletionsModel(
    model=MODEL_ID,       # 这里可以是 SiliconFlow 任意支持的模型 ID
    openai_client=client, # 指向上面的 SiliconFlow client
)

# 定义一个最小 Agent
agent = Agent(
    name="Assistant",
    instructions="你是一个简洁的中文助手，只用中文回答，并说明你是跑在 SiliconFlow 上的。",
    model=model,          # 注意：这里传的是 model 实例，而不是字符串
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "用一句话介绍你自己。")
    print(result.final_output)
