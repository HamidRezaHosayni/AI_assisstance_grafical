import sys
import json
import os
import webbrowser
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.web_researcher.core import perform_web_research

    if __name__ == "__main__":
        try:
            input_data = json.load(sys.stdin)
            query = input_data.get("query")
            if not query or not isinstance(query, str):
                raise ValueError("پارامتر 'query' الزامی و باید رشته باشد.")

            html_path, raw_path = perform_web_research(query, max_results=10)
            webbrowser.open(f"file://{os.path.abspath(html_path)}")

            result = {
                "status": "success",
                "message": f"تحقیق وب درباره «{query}» انجام شد.\nفایل HTML: {html_path}\nفایل متن: {raw_path}"
            }
            print(json.dumps(result, ensure_ascii=False))

        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": f"خطا در web_researcher: {str(e)}"
            }, ensure_ascii=False))
            sys.exit(1)

except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": f"خطای بارگذاری ماژول: {str(e)}"
    }, ensure_ascii=False))
    sys.exit(1)