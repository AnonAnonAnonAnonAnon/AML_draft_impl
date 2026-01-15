#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Doubao + OpenAI Agents SDK demo that calls the local strict-schema tools.
"""

# ===== Config (edit here) =====
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID = "doubao-seed-1-6-251015"
API_KEY = "70f0d563-91a5-4704-a00e-f00cf3a9c864"

RUN_ID = "20260115_192229"
TEST_RUN_ID = f"tools_demo__r{RUN_ID}"
TEST_RUN_DIR = f"logs/tools_demo_run__r{RUN_ID}"
TEST_LOG_REL_PATH = f"logs/tools_demo__r{RUN_ID}.log"
TEST_SLEEP_SECONDS = 60
REQUEST_TIMEOUT_SECS = 60
MAX_TEST_CASES = None  # set to an int or use env TOOL_DEMO_MAX_CASES
ALLOW_FALLBACK_TOOL_DISPATCH = False
RETRY_ON_NO_TOOL_CALLS = 2

ARTIFACTS_BY_KIND = {
    "checkpoint": [f"{TEST_RUN_DIR}/model__r{RUN_ID}.ckpt"],
    "video": [f"{TEST_RUN_DIR}/preview__r{RUN_ID}.mp4"],
    "data_cfg": [f"{TEST_RUN_DIR}/data__r{RUN_ID}.yaml"],
    "train_cfg": [f"{TEST_RUN_DIR}/train__r{RUN_ID}.json"],
    "eval_cfg": [f"{TEST_RUN_DIR}/eval__r{RUN_ID}.yaml"],
    "worklog": [f"{TEST_RUN_DIR}/worklog__r{RUN_ID}.md"],
}

TEST_LOG_LINES = [
    "INFO demo start",
    "WARN something minor",
    "ERROR synthetic failure",
    "INFO demo end",
]

# ===== Code (usually no changes needed) =====
from pathlib import Path
import asyncio
import json
import os
import subprocess
import time

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

from agent_tools_min_strict__r20260115_192229 import (
    run_upsert,
    run_get,
    run_search,
    log_tail,
    log_search,
    run_log_tail,
    run_log_search,
    artifact_find,
    artifact_list,
    proc_status,
    proc_kill,
    resource_gpu,
    resource_disk,
    skill_search,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def prepare_test_files() -> None:
    run_dir = REPO_ROOT / TEST_RUN_DIR
    run_dir.mkdir(parents=True, exist_ok=True)

    for kind, rel_paths in ARTIFACTS_BY_KIND.items():
        for rel_path in rel_paths:
            path = REPO_ROOT / rel_path
            _safe_write(path, f"{kind} placeholder for {RUN_ID}\n")

    log_path = REPO_ROOT / TEST_LOG_REL_PATH
    _safe_write(log_path, "\n".join(TEST_LOG_LINES) + "\n")


client = AsyncOpenAI(
    base_url=ARK_BASE_URL,
    api_key=API_KEY,
    timeout=REQUEST_TIMEOUT_SECS,
)

set_default_openai_api("chat_completions")
set_default_openai_client(client)
set_tracing_disabled(True)


agent = Agent(
    name="ToolCaller",
    instructions=(
        "You are a tool executor. For each user request, call exactly one tool "
        "with the provided parameters. Return only the tool output JSON string. "
        "If tool calling is unavailable, return a JSON object only: "
        "{\"tool\": \"TOOL_NAME\", \"args\": {\"arg\": \"value\"}}."
    ),
    tools=[
        run_upsert,
        run_get,
        run_search,
        log_tail,
        log_search,
        run_log_tail,
        run_log_search,
        artifact_find,
        artifact_list,
        proc_status,
        proc_kill,
        resource_gpu,
        resource_disk,
        skill_search,
    ],
    model=MODEL_ID,
    tool_use_behavior="stop_on_first_tool",
    reset_tool_choice=False,
)

TOOL_MAP = {
    "run_upsert": run_upsert,
    "run_get": run_get,
    "run_search": run_search,
    "log_tail": log_tail,
    "log_search": log_search,
    "run_log_tail": run_log_tail,
    "run_log_search": run_log_search,
    "artifact_find": artifact_find,
    "artifact_list": artifact_list,
    "proc_status": proc_status,
    "proc_kill": proc_kill,
    "resource_gpu": resource_gpu,
    "resource_disk": resource_disk,
    "skill_search": skill_search,
}


def _has_tool_call(result) -> bool:
    for item in getattr(result, "new_items", []):
        if isinstance(item, (ToolCallItem, ToolCallOutputItem)):
            return True
    return False


def _extract_tool_request(text: str) -> dict | None:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _dispatch_tool(tool_name: str, args: dict) -> str:
    tool_fn = TOOL_MAP.get(tool_name)
    if tool_fn is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    payload = json.dumps(args, ensure_ascii=True)
    return asyncio.run(tool_fn.on_invoke_tool(None, payload))


def run_case(label: str, prompt: str, fallback_tool: str, fallback_args: dict) -> str:
    print(f"\n===== {label} =====")
    last_output = ""
    tool_called = False
    for attempt in range(RETRY_ON_NO_TOOL_CALLS + 1):
        if attempt:
            print(f"[retry] attempt {attempt + 1} (no tool calls detected previously)")
        result = Runner.run_sync(agent, prompt)
        last_output = result.final_output
        if _has_tool_call(result):
            tool_called = True
            print(result.final_output)
            return result.final_output

    if not ALLOW_FALLBACK_TOOL_DISPATCH:
        if not tool_called:
            print("[warn] TOOL_NOT_CALLED")
        print(last_output)
        return last_output

    print("[fallback] no tool calls detected; dispatching locally")
    request = _extract_tool_request(last_output)
    if not request:
        request = {"tool": fallback_tool, "args": fallback_args}

    tool_name = request.get("tool", fallback_tool)
    args = request.get("args", fallback_args)
    output = _dispatch_tool(tool_name, args)
    print(output)
    return output


def run_demo() -> None:
    prepare_test_files()

    sleep_proc = subprocess.Popen(["sleep", str(TEST_SLEEP_SECONDS)])
    sleep_pid = sleep_proc.pid

    artifacts_json = json.dumps(ARTIFACTS_BY_KIND, ensure_ascii=True)

    test_cases = [
        (
            "run_upsert",
            (
                "Call run_upsert(run_id='{run_id}', run_dir='{run_dir}', "
                "pids_csv='{pid}', logs_csv='{log_path}', artifacts_json='{artifacts}', "
                "status='demo', note='doubao tool demo'). "
                "If tools are unavailable, return JSON only: "
                "{{\"tool\": \"run_upsert\", \"args\": {{\"run_id\": \"...\"}}}}"
            ).format(
                run_id=TEST_RUN_ID,
                run_dir=TEST_RUN_DIR,
                pid=sleep_pid,
                log_path=TEST_LOG_REL_PATH,
                artifacts=artifacts_json,
            ),
            "run_upsert",
            {
                "run_id": TEST_RUN_ID,
                "run_dir": TEST_RUN_DIR,
                "pids_csv": str(sleep_pid),
                "logs_csv": TEST_LOG_REL_PATH,
                "artifacts_json": artifacts_json,
                "status": "demo",
                "note": "doubao tool demo",
            },
        ),
        (
            "run_get",
            f"Call run_get(run_id='{TEST_RUN_ID}'). If tools are unavailable, "
            "{\"tool\": \"run_get\", \"args\": {\"run_id\": \"...\"}}",
            "run_get",
            {"run_id": TEST_RUN_ID},
        ),
        (
            "run_search",
            f"Call run_search(keyword='{TEST_RUN_ID}', status='demo'). If tools are "
            "unavailable, return JSON only.",
            "run_search",
            {"keyword": TEST_RUN_ID, "status": "demo"},
        ),
        (
            "log_tail",
            f"Call log_tail(path='{TEST_LOG_REL_PATH}', n=10). If tools are "
            "unavailable, return JSON only.",
            "log_tail",
            {"path": TEST_LOG_REL_PATH, "n": 10},
        ),
        (
            "log_search",
            "Call log_search(path='{path}', pattern='ERROR', context=1, max_hits=5).".format(
                path=TEST_LOG_REL_PATH
            ),
            "log_search",
            {
                "path": TEST_LOG_REL_PATH,
                "pattern": "ERROR",
                "context": 1,
                "max_hits": 5,
            },
        ),
        (
            "run_log_tail",
            f"Call run_log_tail(run_id='{TEST_RUN_ID}', n=5).",
            "run_log_tail",
            {"run_id": TEST_RUN_ID, "n": 5},
        ),
        (
            "run_log_search",
            "Call run_log_search(run_id='{run_id}', pattern='WARN', context=1, max_hits=5).".format(
                run_id=TEST_RUN_ID
            ),
            "run_log_search",
            {
                "run_id": TEST_RUN_ID,
                "pattern": "WARN",
                "context": 1,
                "max_hits": 5,
            },
        ),
        (
            "artifact_find",
            "Call artifact_find(run_id='{run_id}', kind='checkpoint', latest=True).".format(
                run_id=TEST_RUN_ID
            ),
            "artifact_find",
            {"run_id": TEST_RUN_ID, "kind": "checkpoint", "latest": True},
        ),
        (
            "artifact_list",
            f"Call artifact_list(run_id='{TEST_RUN_ID}').",
            "artifact_list",
            {"run_id": TEST_RUN_ID},
        ),
        (
            "proc_status",
            f"Call proc_status(run_id='{TEST_RUN_ID}').",
            "proc_status",
            {"run_id": TEST_RUN_ID},
        ),
        (
            "proc_kill",
            f"Call proc_kill(run_id='{TEST_RUN_ID}').",
            "proc_kill",
            {"run_id": TEST_RUN_ID},
        ),
        (
            "resource_disk",
            "Call resource_disk(paths_csv='.').",
            "resource_disk",
            {"paths_csv": "."},
        ),
        ("resource_gpu", "Call resource_gpu().", "resource_gpu", {}),
        (
            "skill_search",
            "Call skill_search(query='robotwin', top_k=3).",
            "skill_search",
            {"query": "robotwin", "top_k": 3},
        ),
        (
            "proc_status_after",
            f"Call proc_status(run_id='{TEST_RUN_ID}').",
            "proc_status",
            {"run_id": TEST_RUN_ID},
        ),
    ]

    max_cases = MAX_TEST_CASES
    env_max = os.environ.get("TOOL_DEMO_MAX_CASES")
    if env_max:
        try:
            max_cases = int(env_max)
        except ValueError:
            max_cases = None
    if max_cases:
        test_cases = test_cases[:max_cases]

    try:
        for label, prompt, fallback_tool, fallback_args in test_cases:
            run_case(label, prompt, fallback_tool, fallback_args)
            if label == "proc_kill":
                time.sleep(0.5)
    finally:
        if sleep_proc.poll() is None:
            sleep_proc.terminate()
            sleep_proc.wait(timeout=5)


if __name__ == "__main__":
    if not API_KEY or API_KEY.startswith("sk-REPLACE_"):
        raise SystemExit("Please set API_KEY at the top of this script.")

    run_demo()
