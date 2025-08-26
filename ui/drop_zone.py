import os

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QLabel


class DropZone(QLabel):
    """Drag and drop zone for audio files."""

    file_dropped = pyqtSignal(str)

    def __init__(self, zone_name, parent=None):
        super().__init__(parent)
        self.zone_name = zone_name
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(100)
        self.reset_style()

    def reset_style(self):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #4a5568;
                border-radius: 8px;
                background-color: #f7fafc;
                color: #4a5568;
                font-size: 12px;
                font-weight: bold;
                padding: 15px;
            }
            QLabel:hover {
                background-color: #edf2f7;
                border-color: #2d3748;
            }
        """)
        self.setText(f"DROP {self.zone_name} HERE\n\nAudio Files: MP3, FLAC, WAV, M4A, OGG, AAC")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #3182ce;
                    border-radius: 8px;
                    background-color: #ebf8ff;
                    color: #2c5aa0;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 15px;
                }
            """)
            self.setText(f"READY - Drop {self.zone_name} Now!")

    def dragLeaveEvent(self, event):
        self.reset_style()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self.is_audio_file(file_path):
                self.show_success()
                self.file_dropped.emit(file_path)
            else:
                self.show_error("Invalid file type!")
        event.acceptProposedAction()

    @staticmethod
    def is_audio_file(path):
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac'}
        return os.path.splitext(path.lower())[1] in audio_extensions

    def show_success(self):
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #22543d;
                border-radius: 8px;
                background-color: #c6f6d5;
                color: #22543d;
                font-size: 12px;
                font-weight: bold;
                padding: 15px;
            }
        """)
        self.setText(f"SUCCESS - {self.zone_name} Loaded!")

    def show_error(self, message):
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #742a2a;
                border-radius: 8px;
                background-color: #fed7d7;
                color: #742a2a;
                font-size: 12px;
                font-weight: bold;
                padding: 15px;
            }
        """)
        self.setText(f"ERROR - {message}")
