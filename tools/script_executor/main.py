import sys
import json
import os

# Ensure module imports work when executed via subprocess from run_tools.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    import core
except Exception as e:
    # چاپ خطا به stdout به شکل JSON تا caller بتواند آن را پردازش کند
    print(json.dumps({
        "status": "error",
        "message": f"Failed to import core module: {str(e)}",
        "traceback": traceback.format_exc() if 'traceback' in globals() else str(e)
    }, ensure_ascii=False))
    sys.exit(1)

def main():
    # بنرهای انسانی را به stderr بفرست تا stdout فقط شامل JSON خروجی ابزار باشد
    print("====================================", file=sys.stderr)
    print("tools execute successfully !!!!!", file=sys.stderr)
    print("====================================", file=sys.stderr)

    try:
        input_data = json.load(sys.stdin)
        task = input_data.get("task")
        dry_run = input_data.get("dry_run", False)

        if not task:
            err = {
                "status": "error",
                "message": "Missing required field: 'task'",
                "code": "",
                "language": ""
            }
            print(json.dumps(err, ensure_ascii=False))
            sys.exit(1)

        result = core.run(task, dry_run=dry_run)
        print(json.dumps(result, ensure_ascii=False))

        if result.get("status") in ("success", "dry_run"):
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "traceback": traceback.format_exc()
        }, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()