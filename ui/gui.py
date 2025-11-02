# project/ui/gui.py
import sys
from speech.tts import text_to_speech  # ← جدید


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont

from llm.ollama_api import OllamaAPI
from speech import VADRecorder, audio_data_to_text

import threading

class Communicator(QObject):
    transcription_ready = pyqtSignal(str)
    model_response_ready = pyqtSignal(str)


class AssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("دستیار هوش مصنوعی")
        self.resize(800, 600)

        QApplication.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        font = QFont("Vazirmatn", 12)
        if not font.exactMatch():
            font = QFont("B Nazanin", 12)
        self.setFont(font)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === کادر چت: متن سیاه، پس‌زمینه سفید ===
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #ccc;
            }
        """)
        main_layout.addWidget(self.chat_display, stretch=1)

        # === StackedWidget برای سوئیچ بین حالت‌ها ===
        self.input_area = QStackedWidget()
        main_layout.addWidget(self.input_area)

        # --- حالت متنی ---
        self.text_widget = QWidget()
        text_layout = QHBoxLayout(self.text_widget)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("پیام خود را بنویسید...")
        self.input_field.returnPressed.connect(self.send_text_message)
        text_layout.addWidget(self.input_field)

        self.send_button = QPushButton("➤")
        self.send_button.setFixedWidth(50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.send_button.clicked.connect(self.send_text_message)
        text_layout.addWidget(self.send_button)

        self.mic_button = QPushButton("🎤")
        self.mic_button.setFixedWidth(40)
        self.mic_button.setStyleSheet("font-size: 16px;")
        self.mic_button.clicked.connect(self.switch_to_voice_mode)
        text_layout.addWidget(self.mic_button)

        # --- حالت صوتی (بدون SVG) ---
        self.voice_widget = QWidget()
        voice_layout = QHBoxLayout(self.voice_widget)

        self.listen_button = QPushButton("▶️ گوش دادن")
        self.listen_button.clicked.connect(self.resume_listening)
        voice_layout.addWidget(self.listen_button)

        self.stop_button = QPushButton("⏹ توقف")
        self.stop_button.clicked.connect(self.stop_voice_listening)
        voice_layout.addWidget(self.stop_button)

        self.back_button = QPushButton("← بازگشت به متن")
        self.back_button.clicked.connect(self.switch_to_text_mode)
        voice_layout.addWidget(self.back_button)

        self.input_area.addWidget(self.text_widget)   # index 0
        self.input_area.addWidget(self.voice_widget)  # index 1

        # ماژول‌ها
        self.ollama_api = OllamaAPI()
        self.vad_recorder = None
        self.is_listening_vad = False
        self.communicator = Communicator()
        self.communicator.transcription_ready.connect(self.handle_transcription)
        self.communicator.model_response_ready.connect(self.display_model_response)

        self.waiting_for_response = False

    # ==================== مدیریت حالت‌ها ====================

    def switch_to_voice_mode(self):
        self.input_area.setCurrentIndex(1)
        self.chat_display.append("<i>حالت صوتی فعال شد.</i>")
        self.scroll_to_bottom()
        self.start_continuous_listening()

    def switch_to_text_mode(self):
        self.stop_voice_listening()
        self.input_area.setCurrentIndex(0)
        self.input_field.setFocus()
        self.chat_display.append("<i>حالت متنی فعال شد.</i>")
        self.scroll_to_bottom()

    def start_continuous_listening(self):
        if not self.is_listening_vad:
            self.is_listening_vad = True
            self.vad_recorder = VADRecorder(
                on_speech_end=self._on_speech_recorded,
                silence_duration=1.0
            )
            self.vad_recorder.start_continuous()
            print("[GUI] گوش دادن پیوسته شروع شد.")

    def resume_listening(self):
        self.start_continuous_listening()
        self.chat_display.append("<i>گوش دادن از سر گرفته شد.</i>")
        self.scroll_to_bottom()

    def stop_voice_listening(self):
        if self.vad_recorder:
            self.vad_recorder.stop()
        self.is_listening_vad = False
        self.chat_display.append("<i>گوش دادن متوقف شد.</i>")
        self.scroll_to_bottom()
        print("[GUI] گوش دادن متوقف شد.")

    # ==================== پردازش صدا و مدل ====================
    
    def _on_speech_recorded(self, audio_data: bytes, sample_rate: int):
        print(f"[GUI] صدا دریافت شد ({len(audio_data)} بایت). در حال تبدیل به متن...")
        text = audio_data_to_text(audio_data, sample_rate, language="fa-IR")
        self.communicator.transcription_ready.emit(text)

    def handle_transcription(self, text: str):
        """پردازش متن دریافتی از STT (حالت صوتی)"""
        if not text or not text.strip():
            print("[GUI] متن خالی است. نادیده گرفته شد.")
            return

        # 1. نمایش پیام کاربر
        self.chat_display.append(f"<b>شما (صوتی):</b> {text}")
        self.scroll_to_bottom()

        # 2. نمایش پیام انتظار
        self.chat_display.append("<i>در انتظار پاسخ مدل...</i>")
        self.waiting_for_response = True
        self.send_button.setEnabled(False)
        self.scroll_to_bottom()

        # 3. ارسال به مدل در Thread پس‌زمینه
        threading.Thread(target=self._request_model_and_emit, args=(text,), daemon=True).start()

    def send_text_message(self):
        text = self.input_field.text().strip()
        if not text:
            return

        # نمایش فوری پیام کاربر
        self.chat_display.append(f"<b>شما:</b> {text}")
        self.input_field.clear()
        self.scroll_to_bottom()  # ✅ اسکرول قبل از ارسال

        # سپس پیام انتظار
        self.chat_display.append("<i>در انتظار پاسخ مدل...</i>")
        self.waiting_for_response = True
        self.send_button.setEnabled(False)
        self.scroll_to_bottom()

        # ارسال به مدل در Thread پس‌زمینه
        threading.Thread(target=self._request_model_and_emit, args=(text,), daemon=True).start()

    def _request_model_and_emit(self, text: str):
        """فراخوانی send_to_model در پس‌زمینه و ارسال سیگنال با نتیجه"""
        try:
            response = self.ollama_api.send_to_model(text)
        except Exception as e:
            response = f"❌ خطا در فراخوانی مدل: {e}"
        # انتشار نتیجه به thread اصلی
        self.communicator.model_response_ready.emit(response)

    def display_model_response(self, response: str):
        """نمایش پاسخ مدل و پخش صدا در حالت صوتی"""
        if self.waiting_for_response:
            current = self.chat_display.toPlainText()
            lines = current.split('\n')
            if lines and "در انتظار پاسخ مدل..." in lines[-1]:
                lines = lines[:-1]
                self.chat_display.setPlainText('\n'.join(lines))
            self.waiting_for_response = False

        self.send_button.setEnabled(True)
        self.chat_display.append(f"<b>دستیار:</b> {response}")
        self.scroll_to_bottom()

        # ✅ پخش صدا فقط در حالت صوتی
        if self.input_area.currentIndex() == 1:  # index 1 = حالت صوتی
            text_to_speech(response)




    # ==================== کمکی ====================

    def scroll_to_bottom(self):
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())