# project/speech/stt.py
import os
import json
import socket
from threading import Thread

# تشخیص آنلاین بودن
def is_online(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False

# === Google Web Speech API (آنلاین) ===
def _recognize_google(audio_data: bytes, sample_rate: int, language="fa-IR") -> str:
    try:
        import speech_recognition as sr
        audio = sr.AudioData(audio_data, sample_rate, 2)  # 16-bit
        recognizer = sr.Recognizer()
        text = recognizer.recognize_google(audio, language=language)
        return text.strip()
    except Exception as e:
        print(f"[STT-Google] خطا: {e}")
        return ""

# === Vosk (آفلاین) ===
_vosk_model = None

def _load_vosk_model():
    global _vosk_model
    if _vosk_model is None:
        from vosk import Model
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-small-fa-0.5")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"مدل Vosk یافت نشد: {model_path}")
        print("[STT-Vosk] بارگذاری مدل فارسی...")
        _vosk_model = Model(model_path)
        print("[STT-Vosk] مدل بارگذاری شد.")
    return _vosk_model

def _recognize_vosk(audio_data: bytes, sample_rate: int) -> str:
    try:
        from vosk import KaldiRecognizer
        import wave, tempfile

        # ذخیره به عنوان WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)
            wav_path = tmp.name

        model = _load_vosk_model()
        rec = KaldiRecognizer(model, sample_rate)

        with open(wav_path, "rb") as f:
            data = f.read()
            if rec.AcceptWaveform(data):
                result = rec.Result()
            else:
                result = rec.FinalResult()

        os.unlink(wav_path)
        res_json = json.loads(result)
        return res_json.get("text", "").strip()

    except Exception as e:
        print(f"[STT-Vosk] خطا: {e}")
        return ""

# === تابع اصلی ===
def audio_data_to_text(audio_data: bytes, sample_rate: int, language="fa-IR") -> str:
    """
    تشخیص گفتار:
    - اگر آنلاین بود → Google Web Speech API (فارسی/انگلیسی)
    - اگر آفلاین بود → Vosk (فقط فارسی)
    """
    print("[STT] بررسی وضعیت اینترنت...")
    online = is_online()

    if online:
        print("[STT] سیستم آنلاین است. استفاده از Google Web Speech API...")
        text = _recognize_google(audio_data, sample_rate, language=language)
        if text:
            print(f"[STT-Google] متن: '{text}'")
            return text
        else:
            print("[STT-Google] شناسایی ناموفق. تلاش با Vosk...")
            return _recognize_vosk(audio_data, sample_rate)
    else:
        print("[STT] سیستم آفلاین است. استفاده از Vosk...")
        text = _recognize_vosk(audio_data, sample_rate)
        if text:
            print(f"[STT-Vosk] متن: '{text}'")
        return text