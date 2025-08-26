from PyQt5.QtCore import pyqtSignal, QThread

from lib.audio_analysis import analyze_file


class AudioLoadWorker(QThread):
    """Worker thread for loading audio files"""

    finished = pyqtSignal(object, dict, str)
    error = pyqtSignal(str, str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """Run audio analysis in background thread."""
        try:
            audio, info = analyze_file(self.file_path)
            self.finished.emit(audio, info, self.file_path)
        except Exception as e:
            self.error.emit(str(e), self.file_path)
