import json
import os
import time
import re
import traceback
import requests
from dotenv import load_dotenv


load_dotenv()  # بارگذاری تنظیمات از فایل .env

# فرض: تاریخچه در ریشه پروژه ذخیره می‌شود
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "conversation.json")

def save_to_history(user_msg: str, assistant_msg: str):
    """ذخیره‌سازی تاریخچه مکالمه (ساده‌شده)"""
    try:
        history = []
        if os.path.exists(HISTORY_PATH):
            try:
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    # اگر فایل خالی یا خراب بود، به جای خطا دادن، history=[] می‌گذاریم
                    try:
                        history = json.load(f)
                        if not isinstance(history, list):
                            history = []
                    except (json.JSONDecodeError, ValueError):
                        history = []
            except Exception:
                history = []

        history.append({"user": user_msg, "assistant": assistant_msg})

        # نگه‌داشتن فقط 10 مکالمه آخر
        if len(history) > 10:
            history = history[-10:]

        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[OLLAMA] ❌ خطا در save_to_history: {e}")
        traceback.print_exc()

class OllamaAPI:
    def __init__(self):
        # استفاده از دو مدل مجزا
        self.action_model = os.getenv("ACTION_MODEL_NAME", "phi4-mini:3.8b")
        self.chat_model = os.getenv("CHAT_MODEL_NAME", "dolphin3:latest")
        self.api_url = os.getenv("API_URL_CHAT", "http://localhost:11434/api/chat")
        # لیست کلیدواژه‌ها و گونه‌های محاوره‌ای (فارسی/انگلیسی)
        self.tool_keywords = os.getenv("TOOL_KEYWORDS", "").split(",")
        # ریشه‌های ساده برای بررسی سریع (fallback)
        self.verb_roots = os.getenv("VERB_ROOTS", "").split(",")

    def _normalize_for_keyword_search(self, text: str) -> str:
        # حذف علائم نگارشی (غیر حرف/عدد/حروف فارسی)، تبدیل به حروف کوچک و یک‌کسره کردن فاصله‌ها
        t = text.lower()
        t = re.sub(r"[^\w\u0600-\u06FF]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return f" {t} "

    def _detect_action(self, user_query: str) -> bool:
        """تشخیص نیاز به ابزار: تطبیق مبتنی بر توکن و fallback ریشه‌ای"""
        try:
            norm_q = self._normalize_for_keyword_search(user_query)
            tokens = [t for t in norm_q.split() if t]
            token_set = set(tokens)

            # 1) تطبیق دقیق توکنی (هر کلیدواژه که همه توکن‌هایش در پرسش باشد)
            for kw in self.tool_keywords:
                norm_kw = self._normalize_for_keyword_search(kw).strip()
                if not norm_kw:
                    continue
                kw_tokens = [t for t in norm_kw.split() if t]
                if not kw_tokens:
                    continue
                # اگر همه توکن‌های کلیدواژه در توکن‌های پرسش باشند => ابزار مورد نیاز است
                if all(tok in token_set for tok in kw_tokens):
                    print(f"[OLLAMA] _detect_action matched tokens for keyword: {kw}")
                    return True
                # همچنین اگر عبارت کلیدواژه به‌عنوان زیررشته وجود داشته باشد
                if f" {norm_kw} " in norm_q:
                    print(f"[OLLAMA] _detect_action matched substring for keyword: {kw}")
                    return True

            # 2) fallback ساده: بررسی ریشه‌های معمول (برای تلفیق‌های فعل/صفت)
            for root in self.verb_roots:
                if f" {root} " in norm_q:
                    print(f"[OLLAMA] _detect_action matched root: {root}")
                    return True
                if root in norm_q:
                    return True

            return False
        except Exception as e:
            print(f"[OLLAMA] ❌ خطا در _detect_action: {e}")
            traceback.print_exc()
            return False

    def send_to_model(self, user_query: str) -> str:
        try:
            # تشخیص نیاز به ابزار
            is_action = self._detect_action(user_query)
            print(f"[OLLAMA] نیاز به ابزار: {is_action}")

            # انتخاب مدل و پرامپت سیستم
            if is_action:
                model = self.action_model
                # پرامپت سیستم: انتظار JSON با نام ابزار
                system_content = (
                    """
                      "You have access to the following tools:\n"
                      "- script_executor: Generate and run a script. Arguments: {\"task\": \"string\", \"dry_run\": false}\n\n"
                      "Rules:\n"
                      "1. Return ONLY a JSON object with \"name\" and \"arguments\".\n"
                      "2. \"name\" MUST be exactly one of: \"create_file\" or \"script_executor\".\n"
                      "3. NEVER invent new tool names.\n"
                      "4. If unsure, use \"script_executor\" with the full user request as \"task\".\n"
                      "5. NO markdown, NO explanation, NO extra text.\n\n"
                      "Example:\n"
                      "{\"name\": \"script_executor\", \"arguments\": {\"task\": \"Create a folder named test on desktop\", \"dry_run\": true}}"

                    """.strip()
                )
            else:
                model = self.chat_model
                # پرامپت سیستم: گفتگوی معمولی
                # پرامپت سیستم: گفتگوی معمولی (انگلیسی برای مدل، فارسی برای کاربر)
                system_content = """
                    You are Jack, a Persian-speaking AI assistant created by Hamidreza.  
                    You respond only in Persian, clearly and briefly — never in English.  
                    Your purpose is to help users with simple tasks and answer questions naturally.  
                    You can create folders, find files, and execute automated scripts upon request.  
                    Your name is Jack.  
                    You support both voice and text interactions.  
                    If asked who made you, say: "I was created by Hamidreza."  
                    If asked what you can do, say: "I can perform simple tasks like creating folders and finding files."  
                    If asked your name, say: "My name is Jack."  
                    If asked how to interact with you, say: "You can talk to me using voice or text."  
                    Always be helpful, polite, and concise. Never explain more than needed. Never use markdown, lists, or extra punctuation.
                    """.strip()
            # آماده‌سازی پیام‌ها و تاریخچه
            messages = []
            history_text = ""
            if os.path.exists(HISTORY_PATH):
                try:
                    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                        try:
                            history = json.load(f)
                        except (json.JSONDecodeError, ValueError):
                            history = []
                        recent_history = history[-5:]
                        for item in recent_history:
                            history_text += f"👤 User: {item.get('user','')}\n🤖 Assistant: {item.get('assistant','')}\n\n"
                except Exception as e:
                    print(f"[OLLAMA] ⚠️ خطا در بارگذاری تاریخچه: {e}")
                    traceback.print_exc()

            if history_text.strip():
                messages.append({
                    "role": "user",
                    "content": f"📝 Previous conversation history:\n{history_text.strip()}"
                })

            messages.append({"role": "system", "content": system_content})
            messages.append({"role": "user", "content": user_query})

            # پایه payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                    "num_predict": 256
                }
            }

            # اگر حالت ابزار بود، ابزارها را اضافه کن
            if is_action:
                try:
                    from .tool_selector import ToolSelector
                    tool_selector = ToolSelector()
                    relevant_tools = tool_selector.select_relevant_tools(user_query, top_k=3)
                    safe_tools = []
                    name_to_schema = {}
                    for t in relevant_tools:
                        if isinstance(t, dict) and "name" in t:
                            tool_entry = {
                                "name": t["name"],
                                "description": t.get("description", "")
                            }
                            if "parameters" in t and isinstance(t["parameters"], dict):
                                tool_entry["parameters"] = t["parameters"]
                                name_to_schema[t["name"]] = t["parameters"]
                            safe_tools.append(tool_entry)

                    if safe_tools:
                        payload["tools"] = safe_tools
                        print(f"[OLLAMA] ✅ ابزارهای ارسالی: {[t['name'] for t in safe_tools]}")

                        # لاگ ابزارها
                        try:
                            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                            logs_dir = os.path.join(base_dir, "logs")
                            os.makedirs(logs_dir, exist_ok=True)
                            log_file = os.path.join(logs_dir, "tools_sent.log")
                            log_entry = {
                                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "user_query": user_query,
                                "tools_sent": safe_tools
                            }
                            with open(log_file, "a", encoding="utf-8") as lf:
                                lf.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                            print(f"[OLLAMA] ✅ ابزارها لاگ شدند: {log_file}")
                        except Exception as e:
                            print(f"[OLLAMA] ⚠️ خطا در لاگ ابزارها: {e}")
                            traceback.print_exc()
                    else:
                        print("[OLLAMA] ⚠️ هیچ ابزار معتبری برای ارسال پیدا نشد.")
                except Exception as e:
                    print(f"[OLLAMA] ⚠️ خطا در انتخاب ابزارها: {e}")
                    traceback.print_exc()

            # ارسال به مدل
            start_time = time.time()
            print("=================================")
            print(payload)
            print("==================================")
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()

            message = data.get("message", {})
            raw = message.get("content", "").strip()
            elapsed = time.time() - start_time
            print(f"[OLLAMA] 🕒 زمان پاسخ: {elapsed:.2f} ثانیه")
            print(f"[OLLAMA] 📤 پاسخ خام: {raw}")

            cleaned_raw = raw.replace("```json", "").replace("```", "").strip()

            # اگر حالت ابزار بود: parse و انتظار {"name", "arguments"}
            if is_action:
                try:
                    parsed = json.loads(cleaned_raw)
                    if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
                        received_name = parsed["name"]
                        args = parsed.get("arguments", {})

                        # تعیین نام نهایی ابزار (مستقیم یا تصحیح‌شده)
                        final_tool_name = None
                        final_args = args

                        # لیست ابزارهای ارسالی (نام معتبر)
                        provided_tool_names = [t["name"] for t in safe_tools]

                        if received_name in provided_tool_names:
                            final_tool_name = received_name
                            schema = name_to_schema.get(received_name, {})
                            norm_args, _, missing = self._validate_and_normalize_arguments(schema, args)
                            if missing:
                                props = schema.get("properties", {}) if isinstance(schema, dict) else {}
                                for m in missing:
                                    p = props.get(m, {})
                                    norm_args[m] = "" if p.get("type") == "string" or not p.get("type") else 0
                            final_args = norm_args
                        else:
                            # تصحیح نام با difflib
                            import difflib
                            candidate = difflib.get_close_matches(received_name, provided_tool_names, n=1, cutoff=0.6)
                            if candidate:
                                final_tool_name = candidate[0]
                                schema = name_to_schema.get(final_tool_name, {})
                                norm_args, _, missing = self._validate_and_normalize_arguments(schema, args)
                                if missing:
                                    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
                                    for m in missing:
                                        p = props.get(m, {})
                                        norm_args[m] = "" if p.get("type") == "string" or not p.get("type") else 0
                                final_args = norm_args

                        # اجرای ابزار و تولید پیام نهایی
                        if final_tool_name:
                            try:
                                from .run_tools import execute_tool
                                exec_result = execute_tool(final_tool_name, final_args)

                                # تحلیل خروجی و تولید پیام کاربرمحور
                                try:
                                    result_json = json.loads(exec_result)
                                    if result_json.get("status") == "success":
                                        user_message = "ابزار با موفقیت اجرا شد."
                                    else:
                                        user_message = "اجرای ابزار با خطا مواجه شد."
                                except json.JSONDecodeError:
                                    # اگر خروجی JSON نبود، ولی اجرا شد → موفقیت
                                    user_message = "ابزار با موفقیت اجرا شد."

                                save_to_history(user_query, user_message)
                                return user_message

                            except Exception as e:
                                error_msg = "اجرای ابزار با خطا مواجه شد."
                                save_to_history(user_query, error_msg)
                                return error_msg
                        else:
                            # نام ابزار کاملاً نامعتبر است
                            error_msg = "اجرای ابزار با خطا مواجه شد."
                            save_to_history(user_query, error_msg)
                            return error_msg

                    else:
                        # پاسخ مدل فرمت ابزار را ندارد → پاسخ متنی
                        save_to_history(user_query, cleaned_raw)
                        return cleaned_raw

                except (json.JSONDecodeError, ValueError):
                    # مدل پاسخ متنی داده (نه JSON)
                    save_to_history(user_query, cleaned_raw)
                    return cleaned_raw
            else:
                # حالت معمولی (غیر ابزار)
                save_to_history(user_query, cleaned_raw)
                return cleaned_raw

        except Exception as e:
            error_msg = f"❌ خطا در ارتباط با مدل یا پردازش درخواست: {e}"
            print(f"[OLLAMA] {error_msg}")
            traceback.print_exc()
            return error_msg

    def _validate_and_normalize_arguments(self, tool_schema: dict, args: dict):
        """
        بر اساس schema (مثل tools.json.parameters) آرگومان‌ها را فیلتر و نرمالایز می‌کند.
        خروجی: (normalized_args: dict, corrections: list[(received_key, mapped_key_or_None)], missing_required: list)
        """
        try:
            if not isinstance(args, dict):
                return {}, [], list(tool_schema.get("required", [])) if schema else []

            props = tool_schema.get("properties", {}) if isinstance(tool_schema, dict) else {}
            allowed_keys = set(props.keys())
            required = set(tool_schema.get("required", [])) if isinstance(tool_schema, dict) else set()

            # ساخت نگاشت ساده از lowercase -> canonical
            key_map = {k.lower(): k for k in allowed_keys}

            normalized = {}
            corrections = []

            for rk, rv in args.items():
                lk = re.sub(r"[^0-9a-zA-Z\u0600-\u06FF]", "", rk).lower()
                if lk in key_map:
                    canonical = key_map[lk]
                    normalized[canonical] = rv
                    if canonical != rk:
                        corrections.append((rk, canonical))
                else:
                    # امتحانِ نگاشتِ رایج (مثلاً contenttype -> content)
                    for cand in allowed_keys:
                        if lk == re.sub(r"[^0-9a-zA-Z\u0600-\u06FF]", "", cand).lower():
                            normalized[cand] = rv
                            corrections.append((rk, cand))
                            break
                    else:
                        # کلید ناشناس — دور می‌ریزیم اما لاگ می‌کنیم
                        corrections.append((rk, None))

            missing = list(required - set(normalized.keys()))
            return normalized, corrections, missing
        except Exception as e:
            print(f"[OLLAMA] ⚠️ خطا در validate arguments: {e}")
            traceback.print_exc()
            return {}, [], list(tool_schema.get("required", [])) if tool_schema else []
