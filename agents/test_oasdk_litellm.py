#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM as backend + OpenAI Agents SDK 最小测试

核心点：
- 不用自己调用 litellm.completion()
- 直接在 Agent.model 里用 LitellmModel(model=..., base_url=..., api_key=...)
依赖：
  pip install -U "openai-agents[litellm]"

"""

# ===== 配置区（按需修改） =====
PROVIDER = "silicon"  # "uiui" / "doubao" / "silicon"
USER_PROMPT = "你好。请用一句话回复我。"

# --- UIUI ---
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"   # 或 "https://api1.uiuiapi.com/v1"
UIUI_MODEL_ID = "openai/gpt-5.2"              # 也可试 "gpt-5.2"；以 UIUI 控制台为准
UIUI_API_KEY  = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"

# --- 豆包（Volcengine）---
DOUBAO_MODEL_ID = "volcengine/doubao-seed-1-6-251015"
DOUBAO_API_KEY  = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

# --- 硅基流动（SiliconFlow）---
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
SILICON_MODEL_ID = "openai/Qwen/Qwen3-VL-235B-A22B-Thinking"
SILICON_API_KEY  = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"

# ===== 代码区（一般不用改） =====
from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel


def make_litellm_model(provider: str) -> LitellmModel:
    if provider == "uiui":
        return LitellmModel(model=UIUI_MODEL_ID, base_url=UIUI_BASE_URL, api_key=UIUI_API_KEY)
    if provider == "doubao":
        # 豆包一般不需要 base_url（LiteLLM 通过 model 前缀 volcengine/ 识别 provider）
        return LitellmModel(model=DOUBAO_MODEL_ID, api_key=DOUBAO_API_KEY)
    if provider == "silicon":
        return LitellmModel(model=SILICON_MODEL_ID, base_url=SILICON_BASE_URL, api_key=SILICON_API_KEY)
    raise ValueError(f"未知 PROVIDER: {provider}")


def main():
    # 重要：禁用 tracing，避免 Agents SDK 试图把 trace 发到 OpenAI（你用的是第三方 Key/端点）
    set_tracing_disabled(True)

    agent = Agent(
        name="Assistant",
        instructions="你是一个简洁的中文助手，只用中文回答。",
        model=make_litellm_model(PROVIDER),
    )

    result = Runner.run_sync(agent, USER_PROMPT)
    print(result.final_output)

if __name__ == "__main__":
    main()
