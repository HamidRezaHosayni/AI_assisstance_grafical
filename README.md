<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant - Python + Ollama + Local Tools</title>
    <style>
        /* CSS ساده برای بهبود خوانایی در محیط‌های غیر گیت‌هاب، اما گیت‌هاب بیشتر استایل خودش را اعمال می‌کند */
        body { font-family: 'Tahoma', 'Vazirmatn', sans-serif; line-height: 1.6; margin: 20px; }
        .container { max-width: 900px; margin: auto; }
        h1, h2, h3 { border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
        code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .developer-info { display: flex; align-items: center; gap: 20px; }
        .developer-image { border-radius: 50%; object-fit: cover; border: 2px solid #ddd; }
        .screenshot-container { text-align: center; }
        .screenshot-container img { border-radius: 10px; margin: 10px; display: inline-block; }
    </style>
</head>
<body>

<div class="container">

    <h1><span style="font-size: 1.2em;">🤖</span> دستیار هوش مصنوعی – Python + Ollama + Local Tools</h1>

    <p>این پروژه یک <strong>دستیار هوش مصنوعی پیشرفته</strong> است که به‌صورت کاملاً محلی (Local) اجرا می‌شود و می‌تواند متن، صوت، دستور، جستجو و ابزارهای مختلف را مدیریت کند. این برنامه با مدل‌های آفلاین Ollama و ابزارهای قابل‌توسعه کار می‌کند.</p>

    <hr>

    <h2><span style="font-size: 1.2em;">🧠</span> معرفی پروژه</h2>

    <p>این دستیار هوشمند قادر است:</p>
    <ul>
        <li>با کاربر از طریق رابط گرافیکی <strong>PyQt6</strong> ارتباط برقرار کند</li>
        <li><strong>پیام‌ها را تحلیل کند</strong> و تشخیص دهد که آیا باید <em>پاسخ دهد</em> یا <em>ابزاری اجرا کند</em></li>
        <li>ابزارهای مختلف را در محیط <strong>ایمن و ایزوله</strong> اجرا کند</li>
        <li>برای تحلیل و فهم زبان از مدل‌های محلی <strong>Ollama</strong> استفاده کند</li>
        <li>ابزارهای جدید را تنها با یک <strong>Prompt</strong> بسازد</li>
        <li>از اجرای کدهای خطرناک جلوگیری کند</li>
        <li>دارای معماری <strong>ماژولار</strong> و کاملاً توسعه‌پذیر باشد</li>
    </ul>

    <hr>

    <h2><span style="font-size: 1.2em;">⭐</span> ویژگی‌های اصلی</h2>

    <ul>
        <li>پشتیبانی از مدل‌های آفلاین Ollama</li>
        <li>تشخیص خودکار اجرای ابزار</li>
        <li>سیستم Trigger هوشمند بر اساس کلمات کلیدی</li>
        <li>ورودی صوتی ← تبدیل گفتار به متن</li>
        <li>خروجی صوتی TTS</li>
        <li>جستجو داخل PDF</li>
        <li>جستجو در وب</li>
        <li>اجرای دستورات در محیط امن</li>
        <li>قابلیت افزودن ابزارهای جدید</li>
        <li>پشتیبانی کامل از فارسی و انگلیسی</li>
    </ul>

    <hr>

    <h2><span style="font-size: 1.2em;">🖼️</span> اسکرین‌شات‌ها</h2>

    <div class="screenshot-container">
        <img src="./picture/1.png" alt="Screenshot 1" width="45%" style="max-width: 400px;" />
        <img src="./picture/2.png" alt="Screenshot 2" width="45%" style="max-width: 400px;" />
    </div>

    <hr>

    <h1><span style="font-size: 1.2em;">⚙️</span> پیش‌نیازها</h1>

    <h2>1️⃣ نصب Ollama</h2>

    <h3><span style="font-size: 1.2em;">✅</span> ویندوز</h3>
    <p>Ollama را از سایت رسمی دانلود و نصب کنید:
        <br>
        <a href="https://ollama.com/download">https://ollama.com/download</a>
    </p>

    <h3><span style="font-size: 1.2em;">✅</span> لینوکس</h3>
    <pre><code>curl -fsSL https://ollama.com/install.sh | sh</code></pre>

    <h2>2️⃣ نصب مدل‌های لازم</h2>

    <p>پس از نصب Ollama، مدل‌های زیر را نصب کنید:</p>
    <pre><code>ollama pull dolphin3:latest
ollama pull phi4-mini:3.8b
ollama pull qwen2.5:7b</code></pre>

    <hr>

    <h2>3️⃣ نصب پکیج‌ها</h2>

    <p>به مسیر اصلی پروژه بروید و ابتدا یک محیط مجازی ایجاد کنید:</p>
    <pre><code>python -m venv venv</code></pre>

    <h3>فعال‌سازی محیط مجازی:</h3>

    <p><span style="font-size: 1.2em;">✅</span> ویندوز:</p>
    <pre><code>venv\Scripts\activate</code></pre>

    <p><span style="font-size: 1.2em;">✅</span> لینوکس / مک:</p>
    <pre><code>source venv/bin/activate</code></pre>

    <hr>

    <h3>نصب وابستگی‌ها:</h3>

    <pre><code>pip install -r requirements.txt</code></pre>

    <hr>

    <h2><span style="font-size: 1.2em;">🚀</span> اجرای برنامه</h2>

    <p>ابتدا محیط مجازی را فعال کنید و سپس فایل اصلی را اجرا کنید:</p>
    <pre><code>python main.py</code></pre>

    <hr>

    <h1><span style="font-size: 1.2em;">🔧</span> ساخت ابزار جدید (Tools)</h1>

    <p>برای ساخت ابزار جدید:</p>

    <h3><span style="font-size: 1.2em;">✔️</span> ساختار پوشه</h3>

    <pre><code>project/
└── tools/
    └── your_tool/
        └── main.py</code></pre>

    <h3><span style="font-size: 1.2em;">✔️</span> فایل main.py باید ورودی JSON از stdin بگیرد</h3>
    <p>و خروجی فقط یک JSON چاپ کند.</p>

    <h3><span style="font-size: 1.2em;">✔️</span> تعریف ابزارها در فایل tools.json انجام می‌شود.</h3>

    <hr>

    <h2><span style="font-size: 1.2em;">📝</span> پرامپت ساخت ابزار</h2>

    <p>در پروژه فایلی وجود دارد به نام:</p>
    <pre><code>create_Tools.txt</code></pre>

    <p>این فایل شامل یک پرامپت کامل برای ساخت ابزار است.<br>
    اگر آن را به مدل بدهید، هر ابزاری که نیاز دارید برای شما تولید می‌کند.</p>

    <hr>

    <h2><span style="font-size: 1.2em;">🗝️</span> نحوه فعال‌سازی ابزارها</h2>

    <p>در فایل <code>.env</code> بخشی به صورت زیر وجود دارد:</p>
    <pre><code>TOOL_KEYWORDS=اجرا کن,بساز,جستجو کن,سرچ,سرچ کن,بگرد,پیدا کن,ذخیره کن,فایل بساز,تولید کن,انجام بده,بنویس,run,create,search,generate,find,save,make file,build,execute,اسکریپت,کد,دستور
VERB_ROOTS=جستجو,سرچ,بگرد,پیدا,بساز,ایجاد,ذخیره,write,create,search,find,run,اسکریپت,کد,دستور</code></pre>

    <p>این کلمات باعث می‌شوند برنامه تشخیص دهد که باید ابزار اجرا شود.</p>

    <hr>

    <h1><span style="font-size: 1.2em;">🧑‍💻</span> معرفی برنامه‌نویس</h1>

    <div class="developer-info">

        <img src="./picture/3.jpg"
            alt="Developer Image"
            width="180"
            height="180"
            class="developer-image" />

        <div>
            <h3><span style="font-size: 1.2em;">👨‍💻</span> برنامه‌نویس پروژه</h3>
            <p><strong>نام:</strong> سید حمیدرضا حسینی</p>
            <p><strong>ایمیل:</strong> hamidrezahosayni22@gmail.com</p>
            <p><strong>وبسایت:</strong> no-website</p>
            <p><strong>گیت‌هاب:</strong>
                <a href="https://github.com/HamidRezaHosayni">github.com/HamidRezaHosayni</a>
            </p>
        </div>

    </div>

</div>

</body>
</html>