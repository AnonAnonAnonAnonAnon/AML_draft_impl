#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal outer-agent tools described in docs/draft_tool_of_agent.txt:
- run registry
- log tools
- artifact finder
- proc tools
- resource tools
- skill search
"""

from pathlib import Path
import json
import os
import re
import shutil
import signal
import subprocess
import time
from typing import Any, Dict, List, Optional

from agents import function_tool


RUN_ID = "20260113_162010"
REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_REGISTRY_PATH = REPO_ROOT / "logs" / f"run_registry__r{RUN_ID}.json"


def _load_registry() -> Dict[str, Dict[str, Any]]:
    if not RUN_REGISTRY_PATH.exists():
        return {}
    try:
        with open(RUN_REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry(registry: Dict[str, Dict[str, Any]]) -> None:
    RUN_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=True, indent=2)


def _abs_path(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (REPO_ROOT / p)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _pid_cmd(pid: int) -> str:
    proc_cmd = Path(f"/proc/{pid}/cmdline")
    if not proc_cmd.exists():
        return ""
    try:
        data = proc_cmd.read_text(encoding="utf-8", errors="ignore")
        return data.replace("\x00", " ").strip()
    except OSError:
        return ""


def _read_lines(path: Path) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().splitlines()
    except OSError:
        return []


@function_tool
def run_upsert(
    run_id: str,
    run_dir: str,
    pids: Optional[List[int]] = None,
    logs: Optional[List[str]] = None,
    artifacts: Optional[Dict[str, List[str]]] = None,
    status: Optional[str] = None,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Upsert a run record into a local registry JSON file.
    """
    registry = _load_registry()
    record = registry.get(run_id, {"run_id": run_id})
    record["run_dir"] = run_dir
    if pids is not None:
        record["pids"] = pids
    if logs is not None:
        record["logs"] = logs
    if artifacts is not None:
        record["artifacts"] = artifacts
    if status is not None:
        record["status"] = status
    if note is not None:
        record["note"] = note
    record["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    registry[run_id] = record
    _save_registry(registry)
    return {"ok": True, "record": record, "registry_path": str(RUN_REGISTRY_PATH)}


@function_tool
def run_get(run_id: str) -> Dict[str, Any]:
    """
    Get a run record from the local registry.
    """
    registry = _load_registry()
    return registry.get(run_id, {})


@function_tool
def run_search(keyword: str = "", status: str = "") -> List[Dict[str, Any]]:
    """
    Search run records by run_id/note keyword and optional status.
    """
    registry = _load_registry()
    keyword = (keyword or "").lower()
    results: List[Dict[str, Any]] = []
    for record in registry.values():
        if status and record.get("status") != status:
            continue
        hay = f"{record.get('run_id', '')} {record.get('note', '')}".lower()
        if keyword and keyword not in hay:
            continue
        results.append(record)
    return results


@function_tool
def log_tail(path: str, n: int = 200) -> Dict[str, Any]:
    """
    Return the last n lines from a log file.
    """
    abs_path = _abs_path(path)
    if not abs_path.exists():
        return {"path": str(abs_path), "text": "", "truncated": False, "error": "not found"}
    lines = _read_lines(abs_path)
    truncated = len(lines) > n
    text = "\n".join(lines[-n:])
    return {"path": str(abs_path), "text": text, "truncated": truncated}


@function_tool
def log_search(
    path: str,
    pattern: str,
    context: int = 3,
    max_hits: int = 50,
) -> List[Dict[str, Any]]:
    """
    Search a log file for a pattern with line context.
    """
    abs_path = _abs_path(path)
    lines = _read_lines(abs_path)
    if not lines:
        return []
    try:
        regex = re.compile(pattern)
    except re.error:
        regex = re.compile(re.escape(pattern))
    hits: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        if regex.search(line):
            start = max(1, idx - context)
            end = min(len(lines), idx + context)
            snippet = lines[start - 1 : end]
            hits.append({"path": str(abs_path), "line_no": idx, "lines": snippet})
            if len(hits) >= max_hits:
                break
    return hits


@function_tool
def run_log_tail(run_id: str, n: int = 200) -> Dict[str, Any]:
    """
    Tail the most recent log for a run_id (if available).
    """
    record = run_get(run_id)
    logs = record.get("logs") or []
    if not logs:
        return {"path": "", "text": "", "truncated": False, "error": "no logs in registry"}
    return log_tail(logs[-1], n=n)


@function_tool
def run_log_search(
    run_id: str,
    pattern: str,
    context: int = 3,
    max_hits: int = 50,
) -> List[Dict[str, Any]]:
    """
    Search all logs for a run_id.
    """
    record = run_get(run_id)
    logs = record.get("logs") or []
    all_hits: List[Dict[str, Any]] = []
    for log_path in logs:
        hits = log_search(log_path, pattern, context=context, max_hits=max_hits)
        all_hits.extend(hits)
        if len(all_hits) >= max_hits:
            return all_hits[:max_hits]
    return all_hits


def _collect_artifacts(run_dir: Path, patterns: List[str]) -> List[str]:
    if not run_dir.exists():
        return []
    matches: List[Path] = []
    for pat in patterns:
        matches.extend(run_dir.rglob(pat))
    results: List[str] = []
    for p in matches:
        if p.is_file():
            results.append(str(p))
    return results


@function_tool
def artifact_find(run_id: str, kind: str, latest: bool = True) -> List[str]:
    """
    Find artifacts for a run by kind. Uses registry first, otherwise scans run_dir.
    """
    record = run_get(run_id)
    artifacts = record.get("artifacts") or {}
    if kind in artifacts:
        return artifacts.get(kind, [])

    run_dir = Path(record.get("run_dir", ""))
    run_dir = _abs_path(str(run_dir))

    patterns = {
        "checkpoint": ["*.ckpt", "*.pt", "*.pth", "*.bin"],
        "video": ["*.mp4", "*.gif", "*.png", "*.jpg", "*.jpeg"],
        "data_cfg": ["*data*.yml", "*data*.yaml", "*data*.json"],
        "train_cfg": ["*train*.yml", "*train*.yaml", "*train*.json"],
        "eval_cfg": ["*eval*.yml", "*eval*.yaml", "*eval*.json"],
        "worklog": ["worklog*.md"],
    }.get(kind, [])

    candidates = _collect_artifacts(run_dir, patterns)
    if not candidates:
        return []
    if not latest:
        return candidates

    newest = max(candidates, key=lambda p: Path(p).stat().st_mtime)
    return [newest]


@function_tool
def artifact_list(run_id: str) -> Dict[str, List[str]]:
    """
    List artifacts by kind for a run.
    """
    kinds = ["checkpoint", "video", "data_cfg", "train_cfg", "eval_cfg", "worklog"]
    return {kind: artifact_find(run_id, kind, latest=False) for kind in kinds}


@function_tool
def proc_status(run_id: str) -> List[Dict[str, Any]]:
    """
    Check whether PIDs recorded for a run are alive.
    """
    record = run_get(run_id)
    pids = record.get("pids") or []
    results: List[Dict[str, Any]] = []
    for pid in pids:
        alive = _pid_alive(pid)
        results.append({"pid": pid, "alive": alive, "cmd": _pid_cmd(pid) if alive else ""})
    return results


@function_tool
def proc_kill(run_id: str) -> Dict[str, List[int]]:
    """
    Send SIGTERM to PIDs recorded for a run.
    """
    record = run_get(run_id)
    pids = record.get("pids") or []
    killed: List[int] = []
    still_alive: List[int] = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    time.sleep(0.2)
    for pid in pids:
        if _pid_alive(pid):
            still_alive.append(pid)
        else:
            killed.append(pid)
    return {"killed": killed, "still_alive": still_alive}


@function_tool
def resource_gpu() -> List[Dict[str, Any]]:
    """
    Return GPU memory usage and per-GPU process list if nvidia-smi is available.
    """
    if shutil.which("nvidia-smi") is None:
        return []
    try:
        gpu_out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=uuid,index,memory.used",
                "--format=csv,noheader,nounits",
            ],
            text=True,
        ).strip()
        proc_out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-compute-apps=gpu_uuid,pid,used_memory",
                "--format=csv,noheader,nounits",
            ],
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return []

    gpu_map: Dict[str, Dict[str, Any]] = {}
    if gpu_out:
        for line in gpu_out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            uuid, index, mem = parts[0], parts[1], parts[2]
            gpu_map[uuid] = {"gpu_id": index, "mem_used": int(mem), "procs": []}

    if proc_out:
        for line in proc_out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            uuid, pid_str, mem = parts[0], parts[1], parts[2]
            if uuid not in gpu_map:
                gpu_map[uuid] = {"gpu_id": uuid, "mem_used": 0, "procs": []}
            entry = gpu_map[uuid]
            try:
                pid = int(pid_str)
                mem_i = int(mem)
            except ValueError:
                continue
            entry["procs"].append({"pid": pid, "mem": mem_i, "cmd": _pid_cmd(pid)})

    return list(gpu_map.values())


@function_tool
def resource_disk(paths: List[str]) -> List[Dict[str, Any]]:
    """
    Return disk usage for a list of paths.
    """
    results: List[Dict[str, Any]] = []
    for p in paths:
        abs_path = _abs_path(p)
        try:
            usage = shutil.disk_usage(abs_path)
        except OSError:
            continue
        results.append(
            {
                "path": str(abs_path),
                "free": usage.free,
                "used": usage.used,
                "total": usage.total,
            }
        )
    return results


@function_tool
def skill_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search local SKILL.md files by keyword.
    """
    query = (query or "").lower()
    tokens = [t for t in re.split(r"\W+", query) if t]
    skill_root = REPO_ROOT / ".codex" / "skills"
    results: List[Dict[str, Any]] = []
    if not skill_root.exists():
        return results

    for root, _, files in os.walk(skill_root):
        if "SKILL.md" not in files:
            continue
        skill_path = Path(root) / "SKILL.md"
        try:
            content = skill_path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            content = ""
        name = Path(root).name
        score = 0
        if tokens:
            for t in tokens:
                score += content.count(t) + name.lower().count(t) * 2
            if score == 0:
                continue
        results.append(
            {
                "name": name,
                "score": score,
                "why": f"matched tokens={tokens}" if tokens else "no query provided",
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
