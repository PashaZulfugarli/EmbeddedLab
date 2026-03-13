import sys
import time
import glob
import serial

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QProgressBar
)

BAUD = 9600


def auto_detect_port():
    ports = glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/cu.usbserial*")
    return ports[0] if ports else None


class SoundMonitorGUI(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Lab 5 — Sound Monitor")

        layout = QVBoxLayout()

        self.levelLabel = QLabel("Sound Level: -")
        self.voltLabel = QLabel("Voltage: -")
        self.statusLabel = QLabel("Status: -")

        self.bar = QProgressBar()
        self.bar.setRange(0, 1023)

        layout.addWidget(self.levelLabel)
        layout.addWidget(self.voltLabel)
        layout.addWidget(self.statusLabel)
        layout.addWidget(self.bar)

        self.setLayout(layout)

        self.ser = None

        self.connect_serial()

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_data)
        self.timer.start(100)

    def connect_serial(self):

        port = auto_detect_port()

        if not port:
            print("Arduino not found")
            return

        try:

            self.ser = serial.Serial(port, BAUD, timeout=0.2)

            time.sleep(2)

            print("Connected to", port)

        except Exception as e:

            print("Connection error:", e)

    def read_data(self):

        if not self.ser:
            return

        if not self.ser.in_waiting:
            return

        line = self.ser.readline().decode(errors="ignore").strip()

        if line.startswith("STATE"):
            return

        try:

            parts = line.split(",")

            level = int(parts[0].split("=")[1])
            volt = float(parts[1].split("=")[1])
            status = parts[2].split("=")[1]

            self.levelLabel.setText(f"Sound Level: {level}")
            self.voltLabel.setText(f"Voltage: {volt:.2f} V")
            self.statusLabel.setText(f"Status: {status}")

            self.bar.setValue(level)

        except:
            pass


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = SoundMonitorGUI()

    window.resize(400, 200)

    window.show()

    sys.exit(app.exec())
