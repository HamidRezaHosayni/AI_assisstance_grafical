# project/llm/run_tools.py
import os
import sys
import json
import subprocess
import traceback
import re

def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    اجرای ابزار با لاگ کامل و تلاش برای استخراج JSON از stdout حتی اگر بنر یا لاگ اضافی چاپ شده باشد.
    """
    try:
        tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
        tool_path = os.path.join(tools_dir, tool_name, "main.py")

        if not os.path.exists(tool_path):
            return json.dumps({
                "status": "error",
                "message": f"ابزار '{tool_name}' یافت نشد.",
                "tool_path": tool_path
            }, ensure_ascii=False)

        tool_cwd = os.path.dirname(tool_path)
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.run(
            [sys.executable, tool_path],
            input=json.dumps(arguments, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=tool_cwd,
            timeout=120,
            env=env
        )

        stdout = (process.stdout or "").strip()
        stderr = (process.stderr or "").strip()
        rc = process.returncode

        debug_info = {
            "tool_name": tool_name,
            "tool_path": tool_path,
            "cwd": tool_cwd,
            "rc": rc,
            "stdout": stdout,
            "stderr": stderr
        }

        # اگر stdout کامل JSON معتبر است، آن را بازگردان
        if stdout:
            try:
                json.loads(stdout)
                return stdout
            except Exception:
                # تلاش برای یافتن اولین/آخرین شیء JSON داخل stdout
                # اولویت: آخرین شیء JSON بزرگ‌تر (معمولاً نتیجه ابزار)
                matches = list(re.finditer(r'(\{(?:.|\n)*\})', stdout, re.DOTALL))
                for m in reversed(matches):
                    candidate = m.group(1)
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        continue

                # در صورت عدم یافتن JSON معتبر، برگردان debug برای دیباگ
                return json.dumps({
                    "status": "error",
                    "message": "tool produced non-JSON stdout",
                    "debug": debug_info
                }, ensure_ascii=False)

        # stdout خالی — اگر stderr وجود دارد، آن را گزارش کن همراه با debug
        if stderr:
            return json.dumps({
                "status": "error",
                "message": "tool produced stderr",
                "debug": debug_info
            }, ensure_ascii=False)

        return json.dumps({
            "status": "error",
            "message": "tool returned no output",
            "debug": debug_info
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"خطا در اجرای ابزار: {str(e)}",
            "traceback": traceback.format_exc()
        }, ensure_ascii=False)


def main():
    """
    تست مستقیم از خط فرمان
    مثال: echo '{"name": "file_creator", "arguments": {"filename": "test.txt", "content": "سلام"}}' | python run_tools.py
    """
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("name")
        arguments = input_data.get("arguments", {})

        if not tool_name:
            print(json.dumps({
                "status": "error",
                "message": "نام ابزار الزامی است."
            }, ensure_ascii=False))
            return

        result = execute_tool(tool_name, arguments)
        print(result)

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"خطا در پردازش ورودی: {str(e)}"
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()