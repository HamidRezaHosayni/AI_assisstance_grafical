# tools/script_executor/utils.py
import os
import platform
from pathlib import Path

def get_desktop_path() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.path.expanduser("~/Desktop"))
    else:
        return Path(os.path.expanduser("~/Desktop"))

def detect_language_from_code(code: str) -> str:
    if not code.strip():
        return "python"
    head = "\n".join(code.strip().splitlines()[:3]).lower()
    if any(kw in head for kw in ["#!/bin/bash", "set ", "echo "]):
        return "bash"
    if any(kw in head for kw in ["get-", "set-", "$", "powershell"]):
        return "powershell"
    return "python"