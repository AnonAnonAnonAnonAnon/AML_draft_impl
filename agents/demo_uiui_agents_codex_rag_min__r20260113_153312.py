#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最小层级 demo（上层 Agent -> 工具函数 -> codex + rag 空函数）：
- 外层：UIUI(OpenAI兼容) + OpenAI Agents SDK（chat.completions）
- 工具：rag_search（占位）
- 工具：codex_exec（subprocess 调 codex exec）
"""

from pathlib import Path
import os
import subprocess

import httpx
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)


# =========================
# CONFIG（只改这里）
# =========================
AGENT_UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
AGENT_MODEL_ID = "gpt-5.2"
AGENT_API_KEY = "sk-REPLACE_WITH_YOUR_UIUI_KEY"
AGENT_TRUST_ENV = True  # True=继承 ALL_PROXY/HTTP_PROXY 等；False=忽略这些环境变量

REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_BIN = os.environ.get("CODEX_BIN", "codex")
CODEX_SANDBOX = os.environ.get("CODEX_SANDBOX", "read-only")
CODEX_STDOUT_MAX_CHARS = 6000


# =========================
# TOOLS
# =========================
@function_tool
def rag_search(query: str) -> str:
    """（占位）RAG 检索：当前不接真实 KB，只返回固定文本。"""
    print(f"[tool:rag_search] query={query!r}")
    return "RAG 占位：当前未接入知识库。"


@function_tool
def codex_exec(prompt: str) -> str:
    """调用 codex CLI 执行一次命令（使用当前系统里已可用的 codex）。"""
    print("[tool:codex_exec] running codex exec ...")
    cmd = [
        CODEX_BIN,
        "exec",
        "--cd",
        str(REPO_ROOT),
        "--sandbox",
        CODEX_SANDBOX,
        prompt,
    ]

    proc = subprocess.run(
        cmd,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if len(stdout) > CODEX_STDOUT_MAX_CHARS:
        stdout = stdout[:CODEX_STDOUT_MAX_CHARS] + "\n...[stdout truncated]..."
    if len(stderr) > CODEX_STDOUT_MAX_CHARS:
        stderr = stderr[:CODEX_STDOUT_MAX_CHARS] + "\n...[stderr truncated]..."

    if proc.returncode == 0:
        return f"[codex ok]\n{stdout}"
    return f"[codex failed] returncode={proc.returncode}\n[stdout]\n{stdout}\n\n[stderr]\n{stderr}"


# =========================
# AGENT
# =========================
def _build_agent() -> Agent:
    http_client = httpx.AsyncClient(trust_env=AGENT_TRUST_ENV)

    client = AsyncOpenAI(
        base_url=AGENT_UIUI_BASE_URL,
        api_key=AGENT_API_KEY,
        http_client=http_client,
    )

    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    set_tracing_disabled(True)

    return Agent(
        name="MiniCoordinator",
        model=AGENT_MODEL_ID,
        tools=[rag_search, codex_exec],
        instructions=(
            "你是一个简洁的中文助手。\n"
            "重要：每次用户提问，你必须按顺序做两步：\n"
            "1) 调用 rag_search(query=用户问题)；\n"
            "2) 调用 codex_exec(prompt=一个对 codex 的指令，要求它回答用户问题)。\n"
            "然后把 rag_search 结果 + codex_exec 结果整合成最终答复。\n"
            "输出结构：\n"
            "- RAG: ...\n"
            "- Codex: ...\n"
            "- Final: ...\n"
        ),
    )


def run_once(user_text: str) -> str:
    agent = _build_agent()
    result = Runner.run_sync(agent, user_text)
    return result.final_output


if __name__ == "__main__":
    if not AGENT_API_KEY or AGENT_API_KEY.startswith("sk-REPLACE_"):
        raise SystemExit("请在脚本顶部配置 AGENT_API_KEY。")

    import sys

    user_query = "你好，用一句话说明你能做什么。"
    if len(sys.argv) >= 2:
        user_query = sys.argv[1]

    print(f"[main] REPO_ROOT={REPO_ROOT}")
    print(f"[main] CODEX_BIN={CODEX_BIN}, CODEX_SANDBOX={CODEX_SANDBOX}")
    print(f"[main] AGENT_UIUI_BASE_URL={AGENT_UIUI_BASE_URL}, AGENT_MODEL_ID={AGENT_MODEL_ID}")
    print(f"[main] user_query={user_query!r}\n")

    out = run_once(user_query)
    print("\n========== FINAL OUTPUT ==========")
    print(out)
