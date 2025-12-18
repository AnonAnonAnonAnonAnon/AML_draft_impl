#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LiteLLM as backend + OpenAI Agents SDK
- 文本/视觉都在一个脚本里跑
- 重点：彻底关闭刷屏（payload/base64/response_cost 报警）
依赖：
  pip install -U "openai-agents[litellm]" litellm
"""

# ====== 0) 一切“降噪设置”必须放在任何三方 import 之前 ======
import os
import logging

# 可选：如果你之前开过代理，这里也顺手清一下
for k in ("ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
    os.environ.pop(k, None)

# 尽量让 LiteLLM/依赖库别走 debug/info（即便不完全命中，也无害）
os.environ.pop("LITELLM_PRINT_STANDARD_LOGGING_PAYLOAD", None)
os.environ.setdefault("LITELLM_LOG", "ERROR")
os.environ.setdefault("LITELLM_LOG_LEVEL", "ERROR")

# 最狠的一刀：直接禁用 Python logging（能拦住绝大部分 logger 输出）
logging.disable(logging.CRITICAL)

def redirect_stdio_forever(logfile: str = "/tmp/litellm_noise.log"):
    """
    把 stdout/stderr 永久重定向到文件（或 os.devnull），并返回“原始终端 fd”
    这样即使后台线程/atexit 继续 print，也只会进 logfile，不会刷屏。
    """
    f = open(logfile, "w")
    old_out = os.dup(1)
    old_err = os.dup(2)
    os.dup2(f.fileno(), 1)
    os.dup2(f.fileno(), 2)
    return old_out, old_err, f

SILENCE = True
OLD_OUT, OLD_ERR, _LOG_F = (None, None, None)
if SILENCE:
    # 想完全丢弃就用 os.devnull；想留证据就用文件
    OLD_OUT, OLD_ERR, _LOG_F = redirect_stdio_forever("/tmp/litellm_noise.log")

def term_print(s: str):
    b = (s + "\n").encode("utf-8", "ignore")
    if OLD_OUT is not None:
        os.write(OLD_OUT, b)
    else:
        print(s)

def term_error(s: str):
    b = (s + "\n").encode("utf-8", "ignore")
    if OLD_ERR is not None:
        os.write(OLD_ERR, b)
    else:
        print(s)

# ====== 1) 现在再 import 三方库（顺序很关键） ======
import base64
import mimetypes

import litellm
# DSPy 常用的降噪开关：只覆盖部分 debug，但建议仍保留 :contentReference[oaicite:3]{index=3}
litellm.suppress_debug_info = True
litellm.set_verbose = False

# 关键：清空 LiteLLM callbacks，避免有人在 callback 里 print 标准 payload/base64 :contentReference[oaicite:4]{index=4}
for attr in ("success_callback", "failure_callback", "service_callback", "callbacks"):
    if hasattr(litellm, attr):
        setattr(litellm, attr, [])

from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel


# ===== 配置区（按需修改） =====
PROVIDER    = "silicon"   # "uiui" / "doubao" / "silicon"
MODE        = "vision"    # "text" / "vision"
USER_PROMPT = "你好。请用一句话回复我。"

IMAGE_PATH  = "/home/liwenbo/projects/AML/AML_draft_impl/agents/image.png"
QUESTION    = "请说明这张图片的主要内容，并列出 3 个关键要素。"

# --- UIUI ---
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
UIUI_MODEL_ID = "openai/gpt-5.2"
UIUI_API_KEY  = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"

# --- 豆包（Volcengine）---
DOUBAO_MODEL_ID = "volcengine/doubao-seed-1-6-251015"
DOUBAO_API_KEY  = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

# --- 硅基流动（SiliconFlow）---
SILICON_BASE_URL = "https://api.siliconflow.cn/v1"
SILICON_MODEL_ID = "openai/Qwen/Qwen3-VL-235B-A22B-Thinking"
SILICON_API_KEY  = "sk-dqhkxlgpjjnhokhsydxiwcwfqgggswisfzcqbuwywccziezl"


def to_data_url(path: str) -> str:
    path = os.path.expanduser(path)
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png"
    with open(path, "rb") as fp:
        b64 = base64.b64encode(fp.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def make_litellm_model(provider: str) -> LitellmModel:
    if provider == "uiui":
        return LitellmModel(model=UIUI_MODEL_ID, base_url=UIUI_BASE_URL, api_key=UIUI_API_KEY)
    if provider == "doubao":
        return LitellmModel(model=DOUBAO_MODEL_ID, api_key=DOUBAO_API_KEY)
    if provider == "silicon":
        return LitellmModel(model=SILICON_MODEL_ID, base_url=SILICON_BASE_URL, api_key=SILICON_API_KEY)
    raise ValueError(f"未知 PROVIDER: {provider}")


def main():
    set_tracing_disabled(True)

    agent = Agent(
        name="Assistant",
        instructions="你是一个简洁的中文助手，只用中文回答。",
        model=make_litellm_model(PROVIDER),
    )

    if MODE == "text":
        r = Runner.run_sync(agent, USER_PROMPT)
        term_print(r.final_output)
        return

    img_data_url = to_data_url(IMAGE_PATH)
    input_items = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": img_data_url}},
            {"type": "text", "text": QUESTION},
        ],
    }]

    r = Runner.run_sync(agent, input_items)
    term_print(r.final_output)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 即使静音，也把异常抛到终端（避免“看起来像没运行”）
        term_error(f"[ERROR] {type(e).__name__}: {e}")
        raise
