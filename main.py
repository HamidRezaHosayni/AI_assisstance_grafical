# project/main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.gui import AssistantGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # تنظیم رنگ‌ها برای تم روشن (اختیاری)
    app.setStyle("Fusion")

    window = AssistantGUI()
    window.show()

    # شروع خودکار حالت گوش دادن (در آینده با STT ترکیب می‌شود)
    # window.start_listening()

    sys.exit(app.exec())