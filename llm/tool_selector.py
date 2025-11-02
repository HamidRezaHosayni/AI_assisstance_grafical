# project/llm/tool_selector.py
import os
import json
import pickle
import numpy as np
import faiss
import requests
import traceback
from dotenv import load_dotenv
import os


class ToolSelector:
    load_dotenv()  # بارگذاری تنظیمات از فایل .env
    def __init__(self, tools_file="tools.json", index_file="tools.index", meta_file="tools_meta.pkl"):
        try:
            # مسیرهای فایل‌ها نسبت به پوشه llm (نرمال‌شده)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            self.tools_file = os.path.join(base_dir, tools_file)
            self.index_file = os.path.join(base_dir, index_file)
            self.meta_file = os.path.join(base_dir, meta_file)

            self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
            self.api_url = os.getenv("API_URL_EMBEDDING", "http://localhost:11434/api/embeddings")
            self.index = None
            self.tools = []

            # بارگذاری یا ایجاد ایندکس
            if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
                print("[TOOL_SELECTOR] فایل‌های ایندکس یافت شدند. بارگذاری از دیسک...")
                self._load_index()
            else:
                print("[TOOL_SELECTOR] فایل ایندکس یافت نشد. ایجاد embedding جدید...")
                self._create_index()
        except Exception as e:
            print(f"[TOOL_SELECTOR] ❌ خطا در init: {e}")
            traceback.print_exc()
            # نگذاریم init کرش کند — ابزارها خالی می‌مانند و index None خواهد بود
            self.index = None
            self.tools = []

    def _get_embedding(self, text: str) -> np.ndarray:
        """دریافت embedding از Ollama API با کنترل خطا"""
        try:
            payload = {
                "model": self.embedding_model,
                "prompt": text
            }
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            emb = data.get("embedding") or data.get("data") or None
            if emb is None:
                print(f"[TOOL_SELECTOR] ⚠️ پاسخ embedding نامعتبر: {data}")
                return np.zeros(768, dtype="float32")
            arr = np.array(emb, dtype="float32")
            # تضمین بعد درست
            if arr.ndim == 1:
                return arr
            # اگر api ساختار متفاوتی داد
            arr = arr.flatten()
            return arr
        except Exception as e:
            print(f"[TOOL_SELECTOR] ❌ خطا در دریافت embedding: {e}")
            traceback.print_exc()
            return np.zeros(768, dtype="float32")


    def _create_index(self):
        try:
            if not os.path.exists(self.tools_file):
                raise FileNotFoundError(f"فایل tools.json یافت نشد در مسیر: {self.tools_file}")

            with open(self.tools_file, "r", encoding="utf-8") as f:
                self.tools = json.load(f)

            print(f"[TOOL_SELECTOR] تولید embedding برای {len(self.tools)} ابزار...")
            embeddings = []
            for i, tool in enumerate(self.tools):
                text = f"{tool.get('name','')}: {tool.get('description','')}"
                emb = self._get_embedding(text)
                if emb is None or emb.size == 0:
                    print(f"[TOOL_SELECTOR] ⚠️ embedding برای ابزار '{tool.get('name')}' ساخته نشد!")
                    emb = np.zeros(768, dtype="float32")
                embeddings.append(emb)

            embeddings = np.array(embeddings, dtype="float32")
            # محافظت در برابر ابعاد نامعتبر
            if embeddings.ndim != 2 or embeddings.shape[0] == 0:
                raise RuntimeError("[TOOL_SELECTOR] قالب embeddings نامعتبر")

            dim = embeddings.shape[1]
            if dim <= 0:
                raise RuntimeError("[TOOL_SELECTOR] بعد embedding غیرمجاز")

            self.index = faiss.IndexFlatL2(dim)
            self.index.add(embeddings)

            faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "wb") as f:
                pickle.dump(self.tools, f)

            print("[TOOL_SELECTOR] ✅ ایندکس جدید ساخته و ذخیره شد.")
        except Exception as e:
            print(f"[TOOL_SELECTOR] ❌ خطا در ایجاد ایندکس: {e}")
            traceback.print_exc()
            # نگه داشتن وضعیت خالی تا برنامه کرش نکند
            self.index = None

    def _load_index(self):
        """بارگذاری ایندکس از دیسک"""
        try:
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, "rb") as f:
                self.tools = pickle.load(f)
            print("[TOOL_SELECTOR] ✅ ایندکس با موفقیت بارگذاری شد.")
        except Exception as e:
            print(f"[TOOL_SELECTOR] ❌ خطا در بارگذاری ایندکس: {e}")
            traceback.print_exc()
            self.index = None
            self.tools = []

    def select_relevant_tools(self, query: str, top_k: int = 3) -> list:
        """جستجوی معنایی و بازگرداندن لیست ابزارهای مرتبط"""
        try:
            if self.index is None:
                print("[TOOL_SELECTOR] ⚠️ ایندکس FAISS در دسترس نیست.")
                return []

            query_vec = self._get_embedding(query)
            if query_vec is None or query_vec.size == 0:
                print("[TOOL_SELECTOR] ⚠️ embedding پرسش ساخته نشد. بازگرداندن لیست خالی.")
                return []

            query_vec = query_vec.reshape(1, -1)
            # در صورت کوچک بودن ابعاد، سعی در اصلاح داریم
            if query_vec.shape[1] != self.index.d:
                print(f"[TOOL_SELECTOR] ⚠️ ابعاد embedding پرسش ({query_vec.shape[1]}) با ایندکس ({self.index.d}) هم‌خوانی ندارد.")
                # اگر اندازه متفاوت است، تلاش برای تطبیق با填 کردن صفر
                if query_vec.shape[1] < self.index.d:
                    pad = np.zeros((1, self.index.d - query_vec.shape[1]), dtype="float32")
                    query_vec = np.concatenate([query_vec, pad], axis=1)
                else:
                    # کوتاه کردن
                    query_vec = query_vec[:, :self.index.d]

            distances, indices = self.index.search(query_vec, top_k)
            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.tools):
                    results.append(self.tools[idx])
            return results
        except Exception as e:
            print(f"[TOOL_SELECTOR] ❌ خطا در select_relevant_tools: {e}")
            traceback.print_exc()
            return []