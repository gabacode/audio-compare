from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QLabel


class LoadingSpinner(QLabel):
    """Simple animated loading spinner widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(60, 60)
        self.hide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_spinner)
        self.spinner_chars = ['◐', '◓', '◑', '◒']
        self.spinner_index = 0

    def start_spinning(self):
        """Start the spinner animation."""
        self.show()
        self.timer.start(100)

    def stop_spinning(self):
        """Stop the spinner animation."""
        self.hide()
        self.timer.stop()

    def update_spinner(self):
        """Update spinner character for animation."""
        char = self.spinner_chars[self.spinner_index]
        self.setText(f'<font size="4" color="#3182ce"><b>{char}</b></font>')
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
