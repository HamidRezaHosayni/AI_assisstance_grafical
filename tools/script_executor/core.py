import os
import sys
import json
import traceback
import subprocess
import requests
import platform
import threading
from pathlib import Path
from dotenv import load_dotenv

# Add script dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# فقط توابع مورد نیاز را import کن
from utils import get_desktop_path, detect_language_from_code

# Load .env
load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent.parent
if (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env", override=True)

OLLAMA_MODEL = os.getenv("MODEL_NAME2", "qwen2.5:7b")
OLLAMA_API_URL = os.getenv("API_URL_CHAT", "http://localhost:11434/api/chat")

# ---------- توابع تأیید اجرا (بدون تغییر) ----------
def _confirm_execution_gui(code: str, language: str) -> bool:
    try:
        from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
            raise RuntimeError("No DISPLAY")
    except Exception:
        return False

    app = QApplication.instance() or QApplication(sys.argv)
    dialog = QDialog()
    dialog.setWindowTitle("تأیید اجرای اسکریپت")
    dialog.resize(800, 600)

    layout = QVBoxLayout(dialog)
    label = QLabel(f"این کد برای اجرا تولید شده ({language}). آیا می‌خواهید اجرا شود؟")
    layout.addWidget(label)

    editor = QTextEdit()
    editor.setReadOnly(True)
    editor.setPlainText(code)
    layout.addWidget(editor)

    btn_layout = QHBoxLayout()
    btn_exec = QPushButton("اجرا")
    btn_cancel = QPushButton("لغو")
    btn_layout.addWidget(btn_exec)
    btn_layout.addWidget(btn_cancel)
    layout.addLayout(btn_layout)

    result = {"approve": False}

    def on_exec():
        result["approve"] = True
        dialog.accept()

    def on_cancel():
        result["approve"] = False
        dialog.reject()

    btn_exec.clicked.connect(on_exec)
    btn_cancel.clicked.connect(on_cancel)

    dialog.exec()
    return result["approve"]

def _confirm_execution_fallback(code: str, language: str) -> bool:
    if os.environ.get("AUTO_APPROVE_SCRIPTS") == "1":
        return True
    try:
        if sys.stdin and sys.stdin.isatty():
            print("\n--- اسکریپت تولید شده ---\n", file=sys.stderr)
            print(code, file=sys.stderr)
            ans = input("آیا مایل به اجرای این اسکریپت هستید؟ (y/n): ").strip().lower()
            return ans in ("y", "yes")
    except Exception:
        pass
    return False

def confirm_execution(code: str, language: str) -> bool:
    if _confirm_execution_gui(code, language):
        return True
    return _confirm_execution_fallback(code, language)

# ---------- تماس با Ollama ----------
def _call_ollama(prompt: str) -> str:
    full_prompt = (
        "You are a code generation engine, NOT a chatbot. "
        "Your ONLY task is to output raw, executable code that fulfills the user's request. "
        "Follow these rules EXACTLY and WITHOUT EXCEPTION:\n"
        "1. Output ONLY the code. NOTHING ELSE.\n"
        "2. NO explanations, NO comments, NO apologies, NO markdown, NO backticks (```).\n"
        "3. DO NOT wrap the code in JSON, XML, or any other structure.\n"
        "4. DO NOT say 'Here is the code:' or 'Sure!' or anything similar.\n"
        "5. If the task is to create a folder, write OS-agnostic Python code using os.makedirs().\n"
        "6. Assume the script will run on the user's desktop. Use relative or standard paths.\n"
        "7. If you are unsure, prefer Python over bash or PowerShell for cross-platform compatibility.\n"
        "8. NEVER include any text before or after the code.\n\n"
        "my username is hamidreza and use linux system"
        f"Task: {prompt}\n\n"
        "BEGIN OUTPUT:"
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": full_prompt}],
        "stream": False,
        "options": {"num_ctx": 2048, "num_predict": 512}
    }
    try:
        resp = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        resp.raise_for_status()
        raw_code = resp.json()["message"]["content"].strip()

        # ✅ حذف backticks و markdown
        if raw_code.startswith("```") and raw_code.endswith("```"):
            # جدا کردن زبان (مثل ```python) و حذف آن
            lines = raw_code.splitlines()
            if len(lines) >= 2:
                cleaned = "\n".join(lines[1:-1])  # اولین و آخرین خط را حذف کن
                raw_code = cleaned.strip()

        return raw_code

    except Exception as e:
        raise RuntimeError(f"خطا در ارتباط با مدل محلی Ollama: {e}")


def generate_code(prompt: str) -> str:
    return _call_ollama(prompt)

# ---------- اجرای اسکریپت ----------
def execute_script_safely(code: str, lang: str, desktop_path: Path, timeout: int = 300) -> dict:
    script_name = f"temp_script_{os.getpid()}"
    if lang == "bash":
        script_file = desktop_path / f"{script_name}.sh"
        cmd = ["bash", str(script_file)]
    elif lang == "powershell":
        script_file = desktop_path / f"{script_name}.ps1"
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_file)]
    else:
        script_file = desktop_path / f"{script_name}.py"
        cmd = [sys.executable, str(script_file)]

    try:
        # تبدیل مسیر به رشته سالم
        desktop_str = str(desktop_path.resolve())
        os.makedirs(desktop_str, exist_ok=True)

        with open(script_file, "w", encoding="utf-8") as f:
            f.write(code)

        safe_env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "USER", "USERNAME", "USERPROFILE")}
        if "USERPROFILE" not in safe_env:
            safe_env["USERPROFILE"] = safe_env.get("HOME", os.path.expanduser("~"))

        result = subprocess.run(
            cmd,
            cwd=str(desktop_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=safe_env
        )

        return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}

    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "اجرای اسکریپت بیش از حد مجاز طول کشید."}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}
    finally:
        try:
            if script_file.exists():
                os.remove(script_file)
        except Exception:
            pass
# ---------- تابع اصلی ----------
def run(task: str, dry_run: bool = False) -> dict:
    try:
        code = generate_code(task)
        if not code:
            return {"status": "error", "message": "مدل هیچ کدی تولید نکرد.", "code": "", "language": ""}

        lang = detect_language_from_code(code)

        if dry_run:
            return {
                "status": "dry_run",
                "message": "کد با موفقیت تولید شد. در انتظار تأیید کاربر.",
                "code": code,
                "language": lang
            }

        approved = confirm_execution(code, lang)
        if not approved:
            return {
                "status": "aborted",
                "message": "کاربر اجرای اسکریپت را لغو کرد.",
                "code": code,
                "language": lang
            }

        # --- اجرای واقعی را در یک thread جداگانه انجام بده ---
        result_container = {}
        desktop = get_desktop_path()

        def _run_script():
            try:
                result_container["output"] = execute_script_safely(code, lang, desktop)
            except Exception as e:
                result_container["error"] = str(e)

        thread = threading.Thread(target=_run_script, daemon=True)
        thread.start()
        thread.join(timeout=300)  # 5 دقیقه

        if thread.is_alive():
            return {
                "status": "error",
                "message": "اجرای اسکریپت بیش از حد مجاز طول کشید.",
                "code": code,
                "language": lang
            }

        if "error" in result_container:
            return {
                "status": "error",
                "message": f"خطا در اجرای اسکریپت: {result_container['error']}",
                "code": code,
                "language": lang
            }

        result = result_container["output"]
        if result["success"]:
            return {
                "status": "success",
                "message": "اسکریپت با موفقیت اجرا شد.",
                "code": code,
                "language": lang,
                "output": result["stdout"]
            }
        else:
            return {
                "status": "error",
                "message": f"اجرای اسکریپت با خطا مواجه شد:\n{result['stderr']}",
                "code": code,
                "language": lang
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "code": "",
            "language": "",
            "traceback": traceback.format_exc() if os.getenv("DEBUG") else None
        }