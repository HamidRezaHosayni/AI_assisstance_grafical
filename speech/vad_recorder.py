# project/speech/vad_recorder.py
import threading
import pyaudio
import webrtcvad

class VADRecorder:
    def __init__(self, on_speech_end=None, silence_duration=0.8):
        self.on_speech_end = on_speech_end
        self.silence_duration = silence_duration
        self.is_active = False
        self._thread = None

        self.RATE = 16000
        self.CHUNK = 320
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(2)

    def start_continuous(self):
        if self.is_active:
            return
        self.is_active = True
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_active = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _record_loop(self):
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            print("[VAD] Stream میکروفون باز شد.")

            while self.is_active:
                frames = []
                silent_chunks = 0
                silence_limit = int(self.silence_duration * self.RATE / self.CHUNK)

                # مرحله ۱: منتظر صدا
                while self.is_active:
                    chunk = stream.read(self.CHUNK)
                    if self.vad.is_speech(chunk, self.RATE):
                        frames.append(chunk)
                        break

                if not self.is_active:
                    break

                # مرحله ۲: ضبط تا سکوت
                while self.is_active:
                    chunk = stream.read(self.CHUNK)
                    frames.append(chunk)
                    if self.vad.is_speech(chunk, self.RATE):
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
                    if silent_chunks > silence_limit:
                        frames = frames[:-silent_chunks]
                        break

                if self.is_active and frames and self.on_speech_end:
                    audio_data = b''.join(frames)
                    self.on_speech_end(audio_data, self.RATE)

            stream.stop_stream()
            print("[VAD] Stream میکروفون بسته شد.")

        except Exception as e:
            print(f"[VAD] خطا: {e}")
        finally:
            audio.terminate()