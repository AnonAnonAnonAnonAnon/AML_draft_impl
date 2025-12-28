# 最简示例
# 豆包 + OpenAI Agent SDK + 视觉问答

# ===== 配置区（按需修改） =====
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID     = "doubao-seed-1-6-251015"   # 豆包推理接入点 ID
API_KEY      = "70f0d563-91a5-4704-a00e-f00cf3a9c864"    # 这里填你的 Ark API Key

# IMAGE_PATH   = "/home/zhangw/AML/AML_draft_impl/agents/image.png"

# ===== CONFIG =====
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent  # agents/ 的上一级通常就是 repo root
IMAGE_PATH = str(THIS_DIR / "image.png")


QUESTION     = "请说明这张图片的主要内容，并列出 3 个关键要素。"


# ===== 代码区（一般不用改） =====
import os
import base64
import mimetypes

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)


def to_data_url(path: str) -> str:
    """把本地图片转成 data URL（data:<mime>;base64,...）"""
    path = os.path.expanduser(path)
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# 用豆包的 OpenAI 兼容接口作为全局 client
client = AsyncOpenAI(
    base_url=ARK_BASE_URL,
    api_key=API_KEY,
)

# 告诉 Agents：底层用 chat.completions，而不是 Responses API
set_default_openai_api("chat_completions")
set_default_openai_client(client)
set_tracing_disabled(True)

# 定义一个多模态 Agent
agent = Agent(
    name="VisionAssistant",
    instructions="你是一个简洁的中文多模态助手，只用中文回答。",
    model=MODEL_ID,   # 直接用豆包模型 / 接入点 ID
)


if __name__ == "__main__":
    # 1. 本地图片 → data URL
    img_data_url = to_data_url(IMAGE_PATH)

    # 2. 构造 Responses 风格 input（input_image + input_text）
    #    Agents 会把它转换成 chat.completions 的 messages，
    #    底层最后还是走豆包的 /chat/completions。
    input_items = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": img_data_url,
                },
                {
                    "type": "input_text",
                    "text": QUESTION,
                },
            ],
        }
    ]

    # 3. 同步跑一轮
    result = Runner.run_sync(agent, input_items)
    print(result.final_output)
