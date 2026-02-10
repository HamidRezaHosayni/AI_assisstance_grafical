import os
import threading
import wave
import numpy as np
import re
from piper.voice import PiperVoice

# مسیر مدل فارسی Piper (نسبت به این فایل)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "fa_tts_model")
MODEL_PATH = os.path.join(MODEL_DIR, "3.onnx")
CONFIG_PATH = os.path.join(MODEL_DIR, "3.json")

# بارگذاری مدل یک‌باره
_piper_voice = None

def _load_piper_model():
    global _piper_voice
    if _piper_voice is None:
        print("[TTS] در حال بارگذاری مدل Piper فارسی...")
        _piper_voice = PiperVoice.load(MODEL_PATH, CONFIG_PATH)
        print("[TTS] مدل Piper بارگذاری شد.")

def extract_persian_text(text: str) -> str:
    """
    فقط کاراکترهای فارسی، اعداد، فاصله و نیم‌فاصله را نگه می‌دارد.
    """
    pattern = r'[^\u0600-\u06FF\u200C\u200D\s0-9\n\r\-]'
    cleaned = re.sub(pattern, ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def _play_audio_file(file_path: str):
    """پخش فایل صوتی با pygame (کراس‌پلتفرم: ویندوز + لینوکس)"""
    try:
        import pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        sound = pygame.mixer.Sound(file_path)
        channel = sound.play()
        while channel.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
    except ImportError:
        print("[TTS] ❌ pygame نصب نیست. لطفاً اجرا کنید: pip install pygame")
    except Exception as e:
        print(f"[TTS] ❌ خطا در پخش صدا: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # حذف فایل موقت (با تأخیر کوتاه برای جلوگیری از خطای "file in use" در ویندوز)
        try:
            import time
            time.sleep(0.1)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"[TTS] ⚠️ خطا در حذف فایل موقت: {e}")

def text_to_speech(text: str):
    """
    تبدیل متن به صدا و پخش آن (فقط در حالت صوتی)
    """
    if not text.strip():
        return

    try:
        _load_piper_model()
        print(f"[TTS] در حال تولید صدا برای: {text}")
        audio_gen = _piper_voice.synthesize(text)

        audio_bytes = b"".join(
            chunk.audio_int16_bytes for chunk in audio_gen 
            if chunk.audio_int16_bytes
        )

        if not audio_bytes:
            print("[TTS] ⚠️ هیچ داده صوتی تولید نشد.")
            return

        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

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