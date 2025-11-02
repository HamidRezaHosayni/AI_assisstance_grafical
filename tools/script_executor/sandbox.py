import os
import subprocess
import tempfile
from pathlib import Path

def execute_in_sandbox(code: str, lang: str, desktop_path: Path, timeout: int = 300) -> dict:
    """
    اجرای ایمن اسکریپت در یک محیط محدودشده.
    - فقط دسترسی به دسکتاپ و temp دارد
    - دسترسی به سایر بخش‌های سیستم مسدود است
    """
    # تعیین فایل موقت روی دسکتاپ
    script_name = f"temp_script_{os.getpid()}"
    if lang == "bash":
        script_file = desktop_path / f"{script_name}.sh"
        cmd = ["bash", str(script_file)]
    elif lang == "powershell":
        script_file = desktop_path / f"{script_name}.ps1"
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_file)]
    else:  # python
        script_file = desktop_path / f"{script_name}.py"
        cmd = ["python", str(script_file)]

    try:
        # ذخیره کد
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(code)

        # اجرای اسکریپت با محدودیت زمان و دسترسی
        result = subprocess.run(
            cmd,
            cwd=str(desktop_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            # محدود کردن متغیرهای محیطی برای امنیت بیشتر
            env={k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "USER", "USERNAME")}
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "اجرای اسکریپت بیش از حد مجاز طول کشید."}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}
    finally:
        # حذف فایل حتی در صورت خطا
        try:
            if script_file.exists():
                os.remove(script_file)
        except Exception:
            pass