# 最简示例
# 豆包 + OpenAI Agent SDK


# ===== 配置区（按需修改） =====
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID    = "doubao-seed-1-6-251015"   # 这里填你的豆包推理接入点 ID
API_KEY     = "70f0d563-91a5-4704-a00e-f00cf3a9c864"         # 这里填你的豆包 Ark API Key

# ===== 代码区（一般不用改） =====
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 用豆包的 OpenAI 兼容接口替换默认 client
client = AsyncOpenAI(
    base_url=ARK_BASE_URL,
    api_key=API_KEY,
)

# 告诉 Agents：用 chat.completions，而不是 Responses API
set_default_openai_api("chat_completions")

# 默认所有 Agent 都走这个豆包 client
set_default_openai_client(client)

# 关掉 tracing（否则会去找 OpenAI 的 key）
set_tracing_disabled(True)

# 定义一个最小 Agent
agent = Agent(
    name="Assistant",
    instructions="你是一个简洁的中文助手，只用中文回答。",
    model=MODEL_ID,   # 直接用模型 / 接入点 ID
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "用一句话介绍你自己。")
    print(result.final_output)
