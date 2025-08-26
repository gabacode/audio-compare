import signal

import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QApplication

from ui.track_panel import TrackPanel


class AudioComparisonApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.track_b = None
        self.track_a = None
        self.init_ui()
        self.setup_signals()

    def init_ui(self):
        self.setWindowTitle("Audio Compare")
        self.setGeometry(100, 100, 1200, 850)
        self.setMinimumSize(1000, 600)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cbd5e0;
                border: 1px solid #a0aec0;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #a0aec0;
            }
        """)

        self.track_a = TrackPanel("Track A", app_ref=self)
        self.track_b = TrackPanel("Track B", app_ref=self)

        splitter.addWidget(self.track_a)
        splitter.addWidget(self.track_b)
        splitter.setSizes([600, 600])

        main_layout.addWidget(splitter)

    def setup_signals(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.close()

    def closeEvent(self, event):
        plt.close('all')
        event.accept()
        QApplication.quit()
