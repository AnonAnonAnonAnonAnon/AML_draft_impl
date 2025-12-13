# ===== 配置区（按需修改） =====
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID    = "doubao-seed-1-6-251015"
API_KEY     = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

# ===== Phoenix tracing：新增 =====
import os
os.environ.setdefault("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")

from phoenix.otel import register
tracer_provider = register(
    project_name="doubao-agents-sdk",
    auto_instrument=True,
)

# 如果你想更“显式”一点，也可以加这两行（可选）
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
OpenAIAgentsInstrumentor().instrument(tracer_provider=tracer_provider)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_trace_processors,     # 新增
)

# 用豆包的 OpenAI 兼容接口替换默认 client
client = AsyncOpenAI(
    base_url=ARK_BASE_URL,
    api_key=API_KEY,
)

# 告诉 Agents：用 chat.completions，而不是 Responses API
set_default_openai_api("chat_completions")
set_default_openai_client(client)

# 关键：替换默认 trace processors，避免发到 OpenAI 后端（也就不会去找 OpenAI key）
set_trace_processors([])

agent = Agent(
    name="Assistant",
    instructions="你是一个简洁的中文助手，只用中文回答。",
    model=MODEL_ID,
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "用一句话介绍你自己。")
    print(result.final_output)
