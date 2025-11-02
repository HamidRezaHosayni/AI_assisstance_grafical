# project/speech/tts.py
import os
import threading
import subprocess
import wave
import numpy as np
from piper.voice import PiperVoice

# مسیر مدل فارسی Piper (نسبت به این فایل)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "fa_tts_model")
MODEL_PATH = os.path.join(MODEL_DIR, "3.onnx")
CONFIG_PATH = os.path.join(MODEL_DIR, "3.json")

# بارگذاری مدل یک‌باره (برای جلوگیری از تأخیر در هر فراخوانی)
_piper_voice = None

def _load_piper_model():
    global _piper_voice
    if _piper_voice is None:
        print("[TTS] در حال بارگذاری مدل Piper فارسی...")
        _piper_voice = PiperVoice.load(MODEL_PATH, CONFIG_PATH)
        print("[TTS] مدل Piper بارگذاری شد.")

def _play_audio_file(file_path: str):
    """پخش فایل صوتی با ffplay (بدون نمایش پنجره)"""
    try:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except FileNotFoundError:
        print("[TTS] ❌ ffplay یافت نشد. لطفاً ffmpeg را نصب کنید.")
    except Exception as e:
        print(f"[TTS] ❌ خطا در پخش صدا: {e}")
    finally:
        # حذف فایل موقت
        try:
            os.remove(file_path)
        except:
            pass

def text_to_speech(text: str):
    """
    تبدیل متن به صدا و پخش آن (فقط در حالت صوتی)
    """
    if not text.strip():
        return

    try:
        # بارگذاری مدل (اولین بار)
        _load_piper_model()

        print(f"[TTS] در حال تولید صدا برای: {text}")
        audio_gen = _piper_voice.synthesize(text)

        # جمع‌آوری داده‌ها
        audio_bytes = b"".join(
            chunk.audio_int16_bytes for chunk in audio_gen 
            if chunk.audio_int16_bytes
        )

        if not audio_bytes:
            print("[TTS] ⚠️ هیچ داده صوتی تولید نشد.")
            return

        # تبدیل به آرایه
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # ذخیره فایل موقت
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            with wave.open(tmp.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                wav_file.writeframes(audio_array.tobytes())
            temp_path = tmp.name

        # پخش در thread جداگانه
        play_thread = threading.Thread(
            target=_play_audio_file,
            args=(temp_path,),
            daemon=True
        )
        play_thread.start()

    except Exception as e:
        print(f"[TTS] ❌ خطا در تولید صدا: {e}")
        import traceback
        traceback.print_exc()