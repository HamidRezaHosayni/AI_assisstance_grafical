<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Assistant – Python + Ollama</title>
</head>
<body style="font-family:Tahoma, sans-serif; line-height:1.8; direction:rtl; background-color:#fff; color:#222; padding:20px;">

<!-- ================= ENGLISH ================= -->

<h1 style="color:#444;">🤖 AI Assistant – Python + Ollama + Local Tools</h1>
<p>This project is an <strong>advanced AI assistant</strong> that runs completely locally and can handle text, voice, commands, search, and various tools. It works with offline Ollama models and extensible tools.</p>

<hr>

<h2 style="color:#444;">🧠 Project Overview</h2>
<ul>
<li>Interact with the user through a <strong>PyQt6 GUI</strong></li>
<li>Analyze messages and determine whether to <em>respond</em> or <em>run a tool</em></li>
<li>Execute tools in a <strong>safe and isolated</strong> environment</li>
<li>Use local <strong>Ollama</strong> models for language understanding</li>
<li>Create new tools using only a <strong>Prompt</strong></li>
<li>Prevent execution of dangerous code</li>
<li>Modular and fully extensible architecture</li>
</ul>

<hr>

<h2 style="color:#444;">⭐ Key Features</h2>
<ul>
<li>Support for offline Ollama models</li>
<li>Automatic tool execution detection</li>
<li>Smart trigger system based on keywords</li>
<li>Voice input → speech-to-text</li>
<li>Text-to-speech output (TTS)</li>
<li>Safe execution of commands in an isolated environment</li>
<li>Ability to add new tools easily</li>
<li>Currently supports Persian language only</li>
</ul>


<hr>

<h2 style="color:#444;">🖼️ Screenshots</h2>
<div style="text-align:center;">
<img src="./picture/1.png" alt="Screenshot 1" style="width:45%; border-radius:10px; margin:10px;" />
<img src="./picture/2.png" alt="Screenshot 2" style="width:45%; border-radius:10px; margin:10px;" />
</div>

<hr>

<h2 style="color:#444;">⚙️ Prerequisites</h2>

<h3 style="color:#444;">1️⃣ Install Ollama</h3>
<h4 style="color:#444;">✅ Windows</h4>
<p>Download from: <a href="https://ollama.com/download" style="color:#1a73e8;">https://ollama.com/download</a></p>

<h4 style="color:#444;">✅ Linux</h4>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">curl -fsSL https://ollama.com/install.sh | sh</pre>

<h3 style="color:#444;">2️⃣ Install Models</h3>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
ollama pull dolphin3:latest
ollama pull phi4-mini:3.8b
ollama pull qwen2.5:7b
</pre>

<h3 style="color:#444;">3️⃣ Install Packages</h3>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux / Mac
pip install -r requirements.txt
</pre>

<hr>

<h2 style="color:#444;">🚀 Run the Program</h2>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">python main.py</pre>

<hr>

<h2 style="color:#444;">🔧 Create New Tools</h2>
<p>Folder structure:</p>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
project/
└── tools/
    └── your_tool/
        └── main.py
</pre>
<p>The <code>main.py</code> file should read JSON from stdin and output JSON only.</p>
<p>Tools are defined in the <code>tools.json</code> file.</p>

<hr>

<h2 style="color:#444;">📝 Tool Creation Prompt</h2>
<p>The file <code>create_Tools.txt</code> contains a complete prompt for creating new tools.</p>

<hr>

<h2 style="color:#444;">🗝️ Activating Tools</h2>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
TOOL_KEYWORDS=run,create,search,...
VERB_ROOTS=search,find,create,...
</pre>

<hr>

<!-- ================= PERSIAN ================= -->

<h1 style="color:#444;">🤖 دستیار هوش مصنوعی – Python + Ollama + Local Tools</h1>
<p>این پروژه یک <strong>دستیار هوش مصنوعی پیشرفته</strong> است که به‌صورت کاملاً محلی (Local) اجرا می‌شود و می‌تواند متن، صوت، دستور، جستجو و ابزارهای مختلف را مدیریت کند. این برنامه با مدل‌های آفلاین Ollama و ابزارهای قابل‌توسعه کار می‌کند.</p>

<hr>

<h2 style="color:#444;">🧠 معرفی پروژه</h2>
<ul>
<li>ارتباط از طریق رابط گرافیکی <strong>PyQt6</strong></li>
<li>تحلیل پیام‌ها و تشخیص پاسخ یا اجرای ابزار</li>
<li>اجرای ابزارها در محیط <strong>ایمن و ایزوله</strong></li>
<li>استفاده از مدل‌های محلی <strong>Ollama</strong></li>
<li>ساخت ابزار جدید با یک <strong>Prompt</strong></li>
<li>جلوگیری از اجرای کدهای خطرناک</li>
<li>معماری <strong>ماژولار</strong> و توسعه‌پذیر</li>
</ul>

<hr>

<h2 style="color:#444;">⭐ ویژگی‌های اصلی</h2>
<ul>
<li>پشتیبانی از مدل‌های آفلاین Ollama</li>
<li>تشخیص خودکار اجرای ابزار</li>
<li>سیستم Trigger هوشمند بر اساس کلمات کلیدی</li>
<li>ورودی صوتی → تبدیل گفتار به متن</li>
<li>خروجی صوتی TTS</li>
<li>اجرای امن دستورات در محیط ایزوله</li>
<li>قابلیت افزودن ابزارهای جدید</li>
<li>در حال حاضر فقط از زبان فارسی پشتیبانی می‌کند</li>
</ul>


<hr>

<h2 style="color:#444;">🖼️ اسکرین‌شات‌ها</h2>
<div style="text-align:center;">
<img src="./picture/1.png" alt="Screenshot 1" style="width:45%; border-radius:10px; margin:10px;" />
<img src="./picture/2.png" alt="Screenshot 2" style="width:45%; border-radius:10px; margin:10px;" />
</div>

<hr>

<h2 style="color:#444;">⚙️ پیش‌نیازها</h2>

<h3 style="color:#444;">1️⃣ نصب Ollama</h3>
<h4 style="color:#444;">✅ ویندوز</h4>
<p>دانلود از: <a href="https://ollama.com/download" style="color:#1a73e8;">https://ollama.com/download</a></p>

<h4 style="color:#444;">✅ لینوکس</h4>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">curl -fsSL https://ollama.com/install.sh | sh</pre>

<h3 style="color:#444;">2️⃣ نصب مدل‌ها</h3>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
ollama pull dolphin3:latest
ollama pull phi4-mini:3.8b
ollama pull qwen2.5:7b
</pre>

<h3 style="color:#444;">3️⃣ نصب پکیج‌ها</h3>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
python -m venv venv
venv\Scripts\activate  # ویندوز
source venv/bin/activate  # لینوکس / مک
pip install -r requirements.txt
</pre>

<hr>

<h2 style="color:#444;">🚀 اجرای برنامه</h2>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">python main.py</pre>

<hr>

<h2 style="color:#444;">🔧 ساخت ابزار جدید (Tools)</h2>
<p>ساختار پوشه:</p>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
project/
└── tools/
    └── your_tool/
        └── main.py
</pre>
<p>ورودی JSON از stdin و خروجی فقط JSON چاپی باشد.</p>
<p>تعریف ابزارها در فایل <code>tools.json</code> انجام می‌شود.</p>

<hr>

<h2 style="color:#444;">📝 پرامپت ساخت ابزار</h2>
<p>فایل <code>create_Tools.txt</code> شامل پرامپت کامل برای ساخت ابزار است.</p>

<hr>

<h2 style="color:#444;">🗝️ نحوه فعال‌سازی ابزارها</h2>
<pre style="background:#f4f4f4; padding:10px; border-radius:5px;">
TOOL_KEYWORDS=اجرا کن,بساز,جستجو کن,...
VERB_ROOTS=جستجو,سرچ,بگرد,...
</pre>

<hr>

<!-- ================= Developer EN ================= -->

<h2 style="color:#444;">🧑‍💻 Developer</h2>
<div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
<img src="./picture/3.jpg" alt="Developer Image" style="width:180px; height:180px; border-radius:50%; object-fit:cover; border:2px solid #ddd;" />
<div>
<h3 style="margin:0;">👨‍💻 Project Developer</h3>
<p><strong>Name:</strong> Seyed HamidReza Hosayni</p>
<p><strong>Email:</strong> <a href="mailto:hamidrezahosayni22@gmail.com" style="color:#1a73e8;">hamidrezahosayni22@gmail.com</a></p>
<p><strong>Website:</strong> no-website</p>
<p><strong>GitHub:</strong> <a href="https://github.com/HamidRezaHosayni" target="_blank" style="color:#1a73e8;">github.com/HamidRezaHosayni</a></p>
</div>
</div>

</body>
</html>
