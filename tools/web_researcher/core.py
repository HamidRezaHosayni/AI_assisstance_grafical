import os
import re
import time
import json
import requests
from pathlib import Path
from ddgs import DDGS
from bs4 import BeautifulSoup

def sanitize_filename(name: str) -> str:
    """تبدیل عنوان به نام فایل ایمن"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:100]

def clean_extracted_text(text: str) -> str:
    """حذف خطوط خالی اضافی و نرمال‌سازی فاصله‌ها"""
    # حذف خطوط خالی چندگانه
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # حذف فاصله‌های ابتدایی و انتهایی هر خط
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    # محدودیت طول (اختیاری برای جلوگیری از prompt طولانی)
    return text[:5000]

def extract_main_content_from_html(html_content: str, url: str) -> str:
    """
    استخراج متن اصلی از صفحه با تمرکز بر تگ‌های معنایی.
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # حذف بخش‌های غیرضروری
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "img", "svg", "noscript"]):
            tag.decompose()
        
        # یافتن بخش محتوای اصلی (با اولویت)
        main_content = None
        for selector in ['main', '[role="main"]', '.content', '#content', '.post', '.article']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body if soup.body else soup

        # استخراج متن از تگ‌های معنایی
        meaningful_texts = []
        allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'code', 'pre', 'td', 'th']
        
        for tag in main_content.find_all(allowed_tags):
            text = tag.get_text(separator=' ', strip=True)
            if text and len(text) > 20:  # فیلتر متن‌های کوتاه بی‌معنی
                meaningful_texts.append(text)
        
        # اگر متنی پیدا نشد، از کل بدنه استفاده کن
        if not meaningful_texts:
            meaningful_texts = [main_content.get_text(separator=' ', strip=True)]
        
        full_text = '\n\n'.join(meaningful_texts)
        return clean_extracted_text(full_text)
        
    except Exception as e:
        return f"[خطا در پردازش HTML صفحه {url}: {str(e)}]"

def call_ollama_generate(prompt: str, model: str = "qwen2.5:7b", max_tokens: int = 1500) -> str:
    """
    فراخوانی مستقیم Ollama برای تولید HTML.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.6
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=300)  # timeout طولانی‌تر
        response.raise_for_status()
        return response.json().get("response", "").strip()
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

    # 2. استخراج و پردازش متن از منابع
    all_sources_data = []
    raw_combined_for_llm = ""
    
    for res in results:
        url = res["href"]
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; WebResearcher/1.0)'}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            resp.encoding = 'utf-8'
            
            # استخراج متن اصلی
            main_text = extract_main_content_from_html(resp.text, url)
            
            source_data = {
                "title": res["title"],
                "url": url,
                "extracted_text": main_text
            }
            all_sources_data.append(source_data)
            
            # برای ارسال به مدل
            raw_combined_for_llm += f"=== منبع: {res['title']} ===\nلینک: {url}\nمتن استخراج‌شده:\n{main_text}\n\n"
            
        except Exception as e:
            error_text = f"[خطا در بارگیری {url}: {str(e)}]"
            all_sources_data.append({
                "title": res["title"],
                "url": url,
                "extracted_text": error_text
            })
            raw_combined_for_llm += f"=== منبع: {res['title']} ===\nلینک: {url}\n{error_text}\n\n"

    # 3. ذخیره فایل متن خام
    raw_file = desktop / f"web_research_{safe_query}_{timestamp}.txt"
    raw_file.write_text(raw_combined_for_llm, encoding="utf-8", errors="replace")

    # 4. ساخت پرامپت هوشمند برای مدل
    prompt = f"""شما یک تحلیلگر حرفه‌ای هستید. اطلاعات زیر از جستجوی وب درباره «{query}» جمع‌آوری شده است.

لطفاً یک گزارش HTML حرفه‌ای و خوانا تولید کنید با این ساختار:

1. یک عنوان اصلی جذاب در بالا
2. یک "خلاصه کلی" که تمام نکات مهم را از همه منابع ترکیب و خلاصه کند
3. یک بخش "جزئیات منبع به منبع" که برای هر منبع:
   - عنوان منبع را نشان دهد
   - متن استخراج‌شده از آن منبع را نمایش دهد
4. یک بخش "منابع" در انتهای صفحه که لیستی از لینک‌های قابل کلیک به همه منابع باشد

قوانین فرمت:
- فقط کد HTML کامل (با <html>, <head> شامل <style>, <body>) بده
- هیچ توضیح یا متن اضافه‌ای در خارج از تگ‌ها ننویس
- از تگ‌های语义ی مثل <header>, <main>, <section>, <article>, <footer> استفاده کن
- استایل داخلی (CSS) با پس‌زمینه تیره، متن سفید/خاکستری روشن، فونت خوانا، فاصله‌گذاری مناسب و direction: rtl

اطلاعات ورودی:
{raw_combined_for_llm[:8000]}"""

    # 5. تولید HTML با مدل
    try:
        html_content = call_ollama_generate(prompt, model="qwen2.5:7b", max_tokens=1500)
    except Exception as e:
        # fallback در صورت خطا
        html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تحقیق وب: {query}</title>
    <style>
        body {{ background: #121212; color: #e0e0e0; font-family: Vazirmatn, sans-serif; line-height: 1.7; padding: 2rem; }}
        h1 {{ color: #4da6ff; margin-bottom: 1rem; }}
        .section {{ margin-bottom: 2rem; }}
        .source-article {{ background: #1e1e1e; padding: 1rem; margin: 1rem 0; border-radius: 8px; }}
        .source-title {{ color: #ff70a6; font-weight: bold; }}
        a {{ color: #4da6ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>تحقیق وب: {query}</h1>
    <p>⚠️ تولید گزارش زیبا با خطا مواجه شد. متن خام در فایل متنی قابل مشاهده است.</p>
    
    <div class="section">
        <h2>جزئیات منبع به منبع</h2>
"""
        for src in all_sources_data:
            html_content += f"""
        <div class="source-article">
            <div class="source-title">{src['title']}</div>
            <p>{src['extracted_text'][:500]}</p>
            <a href="{src['url']}">مشاهده صفحه اصلی</a>
        </div>
"""
        html_content += """
    </div>
    <footer>
        <h2>منابع</h2>
        <ul>
"""
        for src in all_sources_data:
            html_content += f'<li><a href="{src["url"]}">{src["title"]}</a></li>'
        html_content += """
        </ul>
    </footer>
</body>
</html>"""

    # 6. ذخیره فایل HTML
    html_file = desktop / f"web_research_{safe_query}_{timestamp}.html"
    html_file.write_text(html_content, encoding="utf-8", errors="replace")

    return str(html_file), str(raw_file)