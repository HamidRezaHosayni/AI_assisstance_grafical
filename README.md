✅ README — AI Assistant (English + Persian)
🇬🇧 AI Assistant — Intelligent Local & Online Python Assistant
⭐ Introduction

AI Assistant is a powerful, extensible, and fully modular assistant that uses both offline language models (Ollama) and online API-based models (OpenRouter or others) to execute tasks, analyze files, create tools, run code, search documents, perform speech processing, and more.

The program supports voice input, voice output, PDF search, web search, tool-based execution, and the ability to add unlimited custom tools via a dedicated prompt system.

With its flexible architecture, AI Assistant can be used as:

A development helper

A research assistant

A coding agent

A file analyzer

A personal AI desktop app

A modular tool executor

🎯 Features
✅ Core Features

Local model support (Ollama)

Online model support (OpenRouter API)

Multi-model switching (Ollama <-> Online API)

One-click tool execution

Smart tool detection using keywords

Create unlimited custom tools

Search inside PDF files

Web search support

Execute terminal commands

Voice input support

Voice output (TTS)

Automatic conversation memory

GUI-ready architecture

Clear project folder structure

🖼️ Screenshots

(Replace images later by uploading to GitHub and updating URLs)

✅ Main Interface

✅ Tool Execution

✅ PDF/Web Search

⚙️ Prerequisites
✅ Install Ollama

The program requires Ollama to run local LLMs.

🔵 Windows Installation

Download Ollama for Windows:
https://ollama.com/download

Install normally (Next → Next → Finish).

🟣 Linux Installation

Run the following command:

curl -fsSL https://ollama.com/install.sh | sh


After installation verify:

ollama --version

✅ Install Required Models

After Ollama is installed, download these models:

ollama pull dolphin3:latest
ollama pull phi4-mini:3.8b
ollama pull qwen2.5:7b


These models are required for program operation.

📦 Installation
✅ Step 1 — Create Virtual Environment
python3 -m venv venv


Activate it:

Linux:
source venv/bin/activate

Windows:
venv\Scripts\activate

✅ Step 2 — Install Requirements

Go to the root of the project and run:

pip install -r requirements.txt

▶️ Running the Program

Activate your virtual environment:

Linux:
source venv/bin/activate

Windows:
venv\Scripts\activate


Then run:

python main.py


The AI Assistant will start immediately.

🛠️ Creating New Tools

The assistant supports dynamic tool creation.

Inside your project there is a file:

create_Tools.txt


This file contains a powerful prompt template.

✅ How to create a new tool:

Open create_Tools.txt

Copy the entire content

Paste it into your AI model (ChatGPT, LLaMA, etc.)

Describe the tool you want

The model will automatically generate:

Python file

Tool structure

Input/output format

Integration steps

You can create tools such as:

File generators

Web scrapers

Database handlers

PDF processors

Network utilities

Custom automation scripts

The system is unlimited and fully extensible.

🎛️ How Tools Are Activated (Keyword System)

Inside your .env file you have:

TOOL_KEYWORDS=اجرا کن,بساز,جستجو کن,سرچ,سرچ کن,بگرد,پیدا کن,ذخیره کن,فایل بساز,تولید کن,انجام بده,بنویس,run,create,search,generate,find,save,make file,build,execute,اسکریپت,کد,دستور
VERB_ROOTS=جستجو,سرچ,بگرد,پیدا,بساز,ایجاد,ذخیره,write,create,search,find,run,اسکریپت,کد,دستور


Whenever a user types a sentence containing one of these keywords:

✅ The program detects intent
✅ The correct tool is selected
✅ The tool is executed automatically

This is the foundation of tool automation.

🧩 How to Use the Program

Activate the virtual environment

Navigate to the project root

Run:

python main.py


Speak or type your request

If the request includes tool keywords → the tool will run

Otherwise, the LLM will respond normally

👨‍💻 Developer Information
Developer	Contact
HamidReza Hosayni	(Your details here)
📧 Email

your-email@example.com

🌐 Website

https://yourwebsite.com

🖼️ Developer Photo

(Insert your image here)


———————————————————————————
🇮🇷 دستیار هوش مصنوعی — نسخه فارسی
⭐ معرفی

دستیار هوش مصنوعی یک برنامه قدرتمند، قابل توسعه و مجهز به ابزارهای مختلف است که با استفاده از مدل‌های زبانی آفلاین (Ollama) و مدل‌های آنلاین (OpenRouter و …) می‌تواند کارهای مختلفی مانند:

پردازش صدا

تولید صدا

تحلیل فایل‌ها

جستجو داخل PDF

جستجو در وب

اجرای دستورات ترمینال

ساخت ابزارهای جدید

تحلیل کد

اجرای کد

مدیریت مکالمه

را انجام دهد.

این برنامه به صورت تماماً ماژولار طراحی شده است و می‌تواند به عنوان:

✅ دستیار برنامه‌نویسی
✅ دستیار تحقیقاتی
✅ ابزار تحلیل فایل
✅ دستیار آفلاین دسکتاپ
✅ سیستم اجرای ابزارهای پویا

استفاده شود.

🎯 ویژگی‌ها

پشتیبانی از مدل‌های آفلاین

پشتیبانی از API آنلاین

سوئیچ آنی بین مدل‌ها

اجرای ابزار با تشخیص هوشمند

پشتیبانی از صدا

مدیریت تاریخچه مکالمه

پشتیبانی از فایل‌ها و پروژه‌ها

ساخت ابزارهای نامحدود

ساختار استاندارد پوشه‌ها

🖼️ تصاویر برنامه

(بعداً تصاویر را اضافه کنید)

/images/main-ui.png
/images/tools.png
/images/search.png

⚙ پیش‌نیازها
✅ نصب Ollama
ویندوز

نصب از سایت رسمی:
https://ollama.com/download

لینوکس
curl -fsSL https://ollama.com/install.sh | sh

✅ نصب مدل‌ها
ollama pull dolphin3:latest
ollama pull phi4-mini:3.8b
ollama pull qwen2.5:7b

📦 نصب برنامه
ساخت محیط مجازی
python -m venv venv

فعال‌سازی

لینوکس:

source venv/bin/activate


ویندوز:

venv\Scripts\activate

نصب پکیج‌ها
pip install -r requirements.txt

▶️ اجرای برنامه
python main.py


برنامه اجرا شده و آماده استفاده است.

🛠 ساخت ابزار جدید

در پروژه فایلی به نام:

create_Tools.txt


وجود دارد.
این فایل یک پرامپت کامل است که اگر آن را به یک مدل هوش مصنوعی بدهید، برای شما هر ابزاری که بخواهید تولید می‌کند.

🎛 نحوه فعال شدن ابزارها

در فایل .env این بخش وجود دارد:

TOOL_KEYWORDS= ...
VERB_ROOTS= ...


این کلمات، کلمات کلیدی ابزار هستند.
اگر کاربر جمله‌ای شامل این کلمات بنویسد → ابزار اجرا می‌شود.

👨‍💻 معرفی برنامه‌نویس
📷 عکس برنامه‌نویس (سمت راست)

(در آینده تصویر قرار دهید)


📄 اطلاعات (سمت چپ)

نام: حمیدرضا حسینی

ایمیل: your-email@example.com

وب‌سایت: https://yourwebsite.com