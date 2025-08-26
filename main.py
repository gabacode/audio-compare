#!/usr/bin/env python3
import signal
import sys

from PyQt5.QtWidgets import QApplication

from app import AudioComparisonApp


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    window = AudioComparisonApp()
    window.show()

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
