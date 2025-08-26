from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem

from lib.audio_analysis import plot_spectrum, extract_numeric_value
from lib.audio_load_worker import AudioLoadWorker
from ui import DropZone, LoadingSpinner, PlotCanvas


class TrackPanel(QFrame):
    """Panel for displaying and analyzing a single audio track."""

    def __init__(self, track_name, parent=None, app_ref=None):
        super().__init__(parent)
        self.plot_canvas = None
        self.spinner = None
        self.drop_zone = None
        self.tree = None
        self.track_name = track_name
        self.current_audio = None
        self.current_info = None
        self.spectrum_data = None
        self.worker = None
        self.colors = {
            "GREEN": QColor(200, 255, 200),
            "RED": QColor(255, 200, 200),
        }
        self.app_ref = app_ref
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 5px;
            }
        """)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header
        header = QLabel(f"TRACK {self.track_name[-1]}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2d3748; padding: 10px; background-color: #f7fafc; border-radius: 4px;")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(50)
        layout.addWidget(header)

        # Drop zone
        drop_container = QFrame()
        drop_container.setFixedHeight(120)
        drop_layout = QVBoxLayout(drop_container)
        drop_layout.setContentsMargins(0, 0, 0, 0)

        self.drop_zone = DropZone(self.track_name)
        self.spinner = LoadingSpinner()

        drop_layout.addWidget(self.drop_zone)
        drop_layout.addWidget(self.spinner, 0, Qt.AlignCenter)

        layout.addWidget(drop_container)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.header().setFixedHeight(35)
        self.tree.setColumnWidth(0, 160)
        self.tree.setColumnWidth(1, 200)
        self.tree.setStyleSheet("""
            QTreeWidget {
                font-size: 11px;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
            }
            QTreeWidget::item {
                height: 22px;
                padding: 2px;
            }
            QTreeWidget::header {
                height: 35px;
                font-size: 12px;
                font-weight: bold;
                background-color: #f7fafc;
                border-bottom: 2px solid #cbd5e0;
            }
            QTreeWidget::header::section {
                height: 35px;
                padding: 8px;
                border-right: 1px solid #cbd5e0;
            }
        """)
        layout.addWidget(self.tree, 1)

        self.plot_canvas = PlotCanvas(self)
        self.plot_canvas.setFixedHeight(250)
        layout.addWidget(self.plot_canvas)

        self.drop_zone.file_dropped.connect(self.load_file)

    def get_other_track(self):
        """Get the other track panel for comparison."""
        if not self.app_ref:
            return None
        if self.track_name == "Track A":
            return self.app_ref.track_b
        else:
            return self.app_ref.track_a

    def update_tree_with_comparison(self, info):
        """Update metadata tree with comparison highlighting."""
        self.tree.clear()

        other_track = self.get_other_track()
        other_info = other_track.current_info if other_track and other_track.current_info else None

        higher_is_better = {
            "Bitrate": "kbps",
            "Sample Rate": "Hz",
            "Bit Depth": "bit"
        }

        lower_is_better = {
            "Volume (dBFS)": "dB"
        }

        for key, value in info.items():
            item = QTreeWidgetItem([key, str(value)])

            if other_info and key in other_info:
                my_value = extract_numeric_value(value)
                other_value = extract_numeric_value(other_info[key])

                if my_value is not None and other_value is not None:
                    if key in higher_is_better:
                        if my_value > other_value:
                            item.setBackground(1, self.colors["GREEN"])
                            item.setToolTip(1, f"Higher than other track ({other_value})")
                        elif my_value < other_value:
                            item.setBackground(1, self.colors["RED"])
                            item.setToolTip(1, f"Lower than other track ({other_value})")
                    elif key in lower_is_better:
                        if my_value > other_value:
                            item.setBackground(1, self.colors["GREEN"])
                            item.setToolTip(1, f"Better than other track ({other_value} dB)")
                        elif my_value < other_value:
                            item.setBackground(1, self.colors["RED"])
                            item.setToolTip(1, f"Worse than other track ({other_value} dB)")

            self.tree.addTopLevelItem(item)

    def trigger_comparison_update(self):
        """Update comparison colors on both tracks."""
        other_track = self.get_other_track()
        if other_track and other_track.current_info:
            other_track.update_tree_with_comparison(other_track.current_info)

    def update_spectrum_scales(self):
        """Update spectrum scales to match between both tracks."""
        other_track = self.get_other_track()
        if not other_track or not self.spectrum_data or not other_track.spectrum_data:
            return

        my_min = self.spectrum_data['y_min']
        my_max = self.spectrum_data['y_max']
        other_min = other_track.spectrum_data['y_min']
        other_max = other_track.spectrum_data['y_max']

        global_limits = {
            'y_min': min(my_min, other_min),
            'y_max': max(my_max, other_max)
        }

        if self.current_audio:
            plot_spectrum(self.current_audio, self.plot_canvas.axes,
                          f"{self.track_name} Spectrum", global_limits)
            self.plot_canvas.draw()

        if other_track.current_audio:
            plot_spectrum(other_track.current_audio, other_track.plot_canvas.axes,
                          f"{other_track.track_name} Spectrum", global_limits)
            other_track.plot_canvas.draw()

    def load_file(self, file_path):
        """Load an audio file for analysis."""
        print(f"Loading file {file_path} for {self.track_name}")

        self.spinner.start_spinning()

        self.tree.clear()
        self.plot_canvas.axes.clear()
        self.plot_canvas.draw()

        self.worker = AudioLoadWorker(file_path)
        self.worker.finished.connect(self.on_file_loaded)
        self.worker.error.connect(self.on_load_error)
        self.worker.start()

    def on_file_loaded(self, audio, info, file_path):
        """Handle successful file loading."""
        self.spinner.stop_spinning()

        self.current_audio = audio
        self.current_info = info

        self.update_tree_with_comparison(info)
        self.tree.expandAll()

        self.spectrum_data = plot_spectrum(audio, self.plot_canvas.axes, f"{self.track_name} Spectrum")
        self.plot_canvas.draw()

        QTimer.singleShot(2000, self.drop_zone.reset_style)

        self.trigger_comparison_update()
        self.update_spectrum_scales()

    def on_load_error(self, error_message, file_path):
        """Handle file loading errors."""
        print(f"Error loading {file_path}: {error_message}")
        self.spinner.stop_spinning()
        self.drop_zone.show_error(f"Error: {error_message}")
        QTimer.singleShot(3000, self.drop_zone.reset_style)
