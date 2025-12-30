import os
import re
import time
import json
import requests
from pathlib import Path
from ddgs import DDGS
from bs4 import BeautifulSoup

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:100]

def extract_text_from_url(url: str, timeout: int = 10) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; WebResearcher/1.0)'}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:2000]
    except Exception as e:
        return f"[خطا در بارگیری {url}: {str(e)}]"

def call_ollama_generate(prompt: str, model: str = "qwen2.5:7b", max_tokens: int = 1000) -> str:
    """
    فراخوانی مستقیم Ollama API برای تولید متن.
    استفاده از /api/generate به جای /api/chat برای سادگی.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.7
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"خطا در ارتباط با Ollama: {e}")

def perform_web_research(query: str, max_results: int = 10) -> tuple[str, str]:
    desktop = Path.home() / "Desktop"
    safe_query = sanitize_filename(query)
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # 1. جستجو در DuckDuckGo
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                })
                if len(results) >= max_results:
                    break
    except Exception as e:
        raise RuntimeError(f"خطا در جستجو: {e}")

    if not results:
        raise RuntimeError("نتیجه‌ای یافت نشد.")

    # 2. استخراج متن خام
    raw_texts = []
    sources = []
    for res in results:
        url = res["href"]
        text = extract_text_from_url(url)
        raw_texts.append(f"منبع: {res['title']}\nلینک: {url}\nمتن:\n{text}\n{'='*50}")
        sources.append({"title": res["title"], "url": url})

    raw_combined = "\n\n".join(raw_texts)
    raw_file = desktop / f"web_research_{safe_query}_{timestamp}.txt"
    raw_file.write_text(raw_combined, encoding="utf-8", errors="replace")

    # 3. ساخت پرامپت برای تولید HTML
    prompt = f"""شما یک تحلیلگر تحقیق هستید. اطلاعات زیر از جستجوی وب درباره «{query}» جمع‌آوری شده است.
لطفاً یک گزارش HTML حرفه‌ای و خوانا تولید کنید که شامل موارد زیر باشد:
- یک عنوان اصلی جذاب
- یک خلاصه کوتاه در بالا
- بخش‌های منطقی بر اساس موضوعات مشترک
- لیست منابع با لینک‌های قابل کلیک
- استایل داخلی (CSS) با پس‌زمینه تیره، متن سفید/خاکستری روشن، فونت sans-serif فارسی‌پسند، فاصله‌گذاری مناسب

قوانین:
- فقط کد HTML کامل (با <html>, <head> شامل <style>, <body>) بده.
- هیچ توضیح، کامنت یا متن اضافه نده.
- از تگ‌های语义ی مثل <header>, <main>, <section>, <footer> استفاده کن.

اطلاعات خام (فقط برای مرجع):
{raw_combined[:5000]}"""

    # 4. فراخوانی مستقیم Ollama
    try:
        html_content = call_ollama_generate(prompt, model="qwen2.5:7b", max_tokens=1000)
    except Exception as e:
        # fallback ساده در صورت خطا
        html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تحقیق وب: {query}</title>
    <style>
        body {{ 
            background: #121212; 
            color: #e0e0e0; 
            font-family: Vazirmatn, 'Segoe UI', Tahoma, sans-serif; 
            line-height: 1.7; 
            padding: 2rem; 
            direction: rtl;
        }}
        h1 {{ color: #4da6ff; }}
        a {{ color: #ff70a6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .source-list {{ margin-top: 1.5rem; }}
    </style>
</head>
<body>
    <h1>تحقیق وب: {query}</h1>
    <p>⚠️ تولید گزارش زیبا با خطا مواجه شد. متن خام در فایل متنی قابل مشاهده است.</p>
    <div class="source-list">
        <h2>منابع:</h2>
        <ul>
""" + "\n".join([f'<li><a href="{src["url"]}">{src["title"]}</a></li>' for src in sources]) + """
        </ul>
    </div>
</body>
</html>"""

    # 5. ذخیره HTML
    html_file = desktop / f"web_research_{safe_query}_{timestamp}.html"
    html_file.write_text(html_content, encoding="utf-8", errors="replace")

    return str(html_file), str(raw_file)