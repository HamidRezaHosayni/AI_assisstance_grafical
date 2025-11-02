# project/tools/file_creator/main.py
import os
import sys
import json

def create_file(filename: str, content: str="hi hamid", directory: str = None) -> dict:
    """
    ایجاد فایل جدید با محتوای مشخص
    """
    try:
        # تعیین مسیر نهایی
        if directory:
            os.makedirs(directory, exist_ok=True)
            full_path = os.path.join(directory, filename)
        else:
            full_path = filename

        # ایجاد فایل
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"فایل '{full_path}' با موفقیت ایجاد شد.",
            "path": os.path.abspath(full_path)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"خطا در ایجاد فایل: {str(e)}"
        }

if __name__ == "__main__":
    # دریافت آرگومان‌ها از stdin (به صورت JSON)
    try:
        input_data = json.load(sys.stdin)
        filename = input_data.get("filename")
        content = input_data.get("content")
        directory = input_data.get("directory")

        if not filename or not content:
            print(json.dumps({
                "status": "error",
                "message": "نام فایل و محتوا الزامی هستند."
            }, ensure_ascii=False))
            sys.exit(1)

        result = create_file(filename, content, directory)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"خطا در پردازش ورودی: {str(e)}"
        }, ensure_ascii=False))
        sys.exit(1)