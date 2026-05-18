import sys
import sqlite3
from datetime import datetime

import serial
import serial.tools.list_ports

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QGroupBox,
    QFrame,
    QSizePolicy,
    QSpacerItem,
)
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon


DATABASE_FILE = "rfid_database.db"
BAUD_RATE = 9600
DATA_PREFIX = "DATA_PACKET:"



APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0B0E14;
    color: #C9D1D9;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 13px;
}

/* ---- Group Boxes ---- */
QGroupBox {
    background-color: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 12px 10px 12px;
    font-size: 11px;
    font-weight: 600;
    color: #8B949E;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -1px;
    padding: 0 6px;
    background-color: #161B22;
    color: #8B949E;
}

/* ---- Labels ---- */
QLabel {
    color: #8B949E;
    font-size: 13px;
}

/* ---- ComboBox ---- */
QComboBox {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 7px;
    padding: 7px 12px;
    color: #E6EDF3;
    font-size: 13px;
    min-width: 220px;
}
QComboBox:hover {
    border-color: #58A6FF;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox QAbstractItemView {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E6EDF3;
    selection-background-color: #1F6FEB;
    padding: 4px;
}

/* ---- Line Edit (Search) ---- */
QLineEdit {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 7px;
    padding: 7px 12px;
    color: #E6EDF3;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #58A6FF;
    background-color: #0D1117;
}
QLineEdit::placeholder {
    color: #484F58;
}

/* ---- Buttons ---- */
QPushButton {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 7px;
    padding: 7px 16px;
    color: #C9D1D9;
    font-size: 13px;
    font-weight: 500;
    min-width: 90px;
}
QPushButton:hover {
    background-color: #30363D;
    border-color: #8B949E;
    color: #E6EDF3;
}
QPushButton:pressed {
    background-color: #161B22;
}
QPushButton:disabled {
    background-color: #161B22;
    color: #484F58;
    border-color: #21262D;
}

QPushButton#connectBtn {
    background-color: #196C2E;
    border-color: #238636;
    color: #3FB950;
    font-weight: 600;
}
QPushButton#connectBtn:hover {
    background-color: #238636;
    color: #AFFFB7;
}

QPushButton#disconnectBtn {
    background-color: #6E1A1A;
    border-color: #B91C1C;
    color: #F87171;
    font-weight: 600;
}
QPushButton#disconnectBtn:hover {
    background-color: #B91C1C;
    color: #FECACA;
}

QPushButton#clearBtn {
    background-color: #3A2500;
    border-color: #92400E;
    color: #F59E0B;
    font-weight: 600;
}
QPushButton#clearBtn:hover {
    background-color: #92400E;
    color: #FDE68A;
}

QPushButton#refreshBtn {
    background-color: #1C3A5E;
    border-color: #1F6FEB;
    color: #58A6FF;
}
QPushButton#refreshBtn:hover {
    background-color: #1F6FEB;
    color: #FFFFFF;
}

/* ---- Table ---- */
QTableWidget {
    background-color: #0D1117;
    border: 1px solid #21262D;
    border-radius: 8px;
    gridline-color: #21262D;
    color: #E6EDF3;
    font-size: 13px;
    selection-background-color: #1F3A5F;
    selection-color: #E6EDF3;
    alternate-background-color: #131920;
}
QTableWidget::item {
    padding: 8px 6px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #1F3A5F;
    color: #58A6FF;
}
QHeaderView::section {
    background-color: #161B22;
    color: #8B949E;
    border: none;
    border-bottom: 1px solid #30363D;
    border-right: 1px solid #21262D;
    padding: 10px 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QHeaderView::section:last {
    border-right: none;
}

/* ---- Log / Text Edit ---- */
QTextEdit {
    background-color: #0D1117;
    border: 1px solid #21262D;
    border-radius: 8px;
    color: #3FB950;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

/* ---- Scrollbars ---- */
QScrollBar:vertical {
    background: #0D1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #30363D;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #58A6FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0D1117;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #30363D;
    border-radius: 4px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ---- Message Box ---- */
QMessageBox {
    background-color: #161B22;
    color: #E6EDF3;
}
QMessageBox QPushButton {
    min-width: 70px;
}
"""




class DatabaseManager:
    def __init__(self, db_file=DATABASE_FILE):
        self.db_file = db_file
        self.initialize_database()

    def connect(self):
        return sqlite3.connect(self.db_file)

    def initialize_database(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_id TEXT UNIQUE,
                rfid_uid TEXT UNIQUE NOT NULL,
                scan_count INTEGER NOT NULL DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_or_update_tag(self, rfid_uid):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, tag_id, scan_count FROM tags WHERE rfid_uid = ?",
            (rfid_uid,)
        )
        existing_tag = cursor.fetchone()

        if existing_tag:
            db_id, tag_id, scan_count = existing_tag
            new_count = scan_count + 1
            cursor.execute("""
                UPDATE tags SET scan_count = ?, last_seen = ? WHERE rfid_uid = ?
            """, (new_count, now, rfid_uid))
            conn.commit()
            conn.close()
            return {"status": "existing", "tag_id": tag_id, "rfid_uid": rfid_uid, "scan_count": new_count}
        else:
            cursor.execute("""
                INSERT INTO tags (tag_id, rfid_uid, scan_count, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?)
            """, ("TEMP", rfid_uid, 1, now, now))
            new_db_id = cursor.lastrowid
            tag_id = f"TAG-{new_db_id:03d}"
            cursor.execute("UPDATE tags SET tag_id = ? WHERE id = ?", (tag_id, new_db_id))
            conn.commit()
            conn.close()
            return {"status": "new", "tag_id": tag_id, "rfid_uid": rfid_uid, "scan_count": 1}

    def get_all_tags(self, search_text=""):
        conn = self.connect()
        cursor = conn.cursor()
        if search_text:
            p = f"%{search_text}%"
            cursor.execute("""
                SELECT tag_id, rfid_uid, scan_count, first_seen, last_seen
                FROM tags WHERE tag_id LIKE ? OR rfid_uid LIKE ?
                ORDER BY id ASC
            """, (p, p))
        else:
            cursor.execute("""
                SELECT tag_id, rfid_uid, scan_count, first_seen, last_seen
                FROM tags ORDER BY id ASC
            """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def clear_database(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tags")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tags'")
        conn.commit()
        conn.close()




class SerialReaderThread(QThread):
    tag_scanned = pyqtSignal(str)
    serial_message = pyqtSignal(str)
    connection_error = pyqtSignal(str)

    def __init__(self, port_name, baud_rate=BAUD_RATE):
        super().__init__()
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.running = False
        self.serial_connection = None

    def run(self):
        try:
            self.serial_connection = serial.Serial(self.port_name, self.baud_rate, timeout=1)
            self.running = True
            self.serial_message.emit(f"Connected to {self.port_name} at {self.baud_rate} baud.")

            while self.running:
                try:
                    line = self.serial_connection.readline().decode(errors="ignore").strip()
                    if not line:
                        continue
                    self.serial_message.emit(f"Arduino › {line}")
                    if line.startswith(DATA_PREFIX):
                        uid = line.replace(DATA_PREFIX, "").strip().upper()
                        if uid:
                            self.tag_scanned.emit(uid)
                except Exception as e:
                    self.connection_error.emit(f"Read error: {e}")
                    break
        except Exception as e:
            self.connection_error.emit(f"Could not open port: {e}")
        finally:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            self.serial_message.emit("Serial connection closed.")

    def stop(self):
        self.running = False
        self.wait()



class StatusBadge(QLabel):
    """Pill-shaped status indicator with colour coding."""

    STYLES = {
        "disconnected": ("● DISCONNECTED", "#484F58", "#21262D", "#30363D"),
        "connected":    ("● CONNECTED",    "#3FB950", "#196C2E", "#238636"),
        "error":        ("● ERROR",        "#F85149", "#6E1A1A", "#B91C1C"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)
        self.set_state("disconnected")

    def set_state(self, state: str):
        text, fg, bg, border = self.STYLES.get(state, self.STYLES["disconnected"])
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 14px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.2px;
            }}
        """)



class StatCard(QFrame):
    """Small card showing a single stat (label + value)."""

    def __init__(self, title: str, value: str = "—", accent: str = "#58A6FF"):
        super().__init__()
        self.accent = accent
        self.setFixedHeight(72)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #161B22;
                border: 1px solid #21262D;
                border-left: 3px solid {accent};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(2)

        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet(
            "font-size: 10px; font-weight: 600; color: #484F58; letter-spacing: 1.2px; background: transparent; border: none;"
        )

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {accent}; background: transparent; border: none;"
        )

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        self.value_label.setText(value)



class RFIDDatabaseGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.serial_thread = None
        self._total_scans = 0
        self._unique_tags = 0

        self.setWindowTitle("RFID Security — Tag Database")
        self.setMinimumSize(1050, 720)

        self.setup_ui()
        self.load_ports()
        self.refresh_table()

    def setup_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        header = self._build_header()
        root_layout.addWidget(header)

        stats_row = self._build_stats_row()
        root_layout.addLayout(stats_row)

        serial_group = self._build_serial_group()
        root_layout.addWidget(serial_group)

        nav_group = self._build_nav_group()
        root_layout.addWidget(nav_group)

        self.table = self._build_table()
        root_layout.addWidget(self.table, stretch=1)

        bottom_row = self._build_bottom_row()
        root_layout.addLayout(bottom_row)

        self.setCentralWidget(root)

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setFixedHeight(52)
        frame.setStyleSheet("""
            QFrame {
                background-color: #161B22;
                border: 1px solid #21262D;
                border-radius: 10px;
            }
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 0, 18, 0)

        icon_label = QLabel("⬡")
        icon_label.setStyleSheet(
            "font-size: 22px; color: #58A6FF; background: transparent; border: none;"
        )

        title = QLabel("RFID Security System")
        title.setStyleSheet(
            "font-size: 17px; font-weight: 700; color: #E6EDF3; background: transparent; border: none;"
        )

        subtitle = QLabel("Tag Database Viewer")
        subtitle.setStyleSheet(
            "font-size: 12px; color: #484F58; background: transparent; border: none;"
        )

        self.status_badge = StatusBadge()

        layout.addWidget(icon_label)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(self.status_badge)

        return frame

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self.card_unique   = StatCard("Unique Tags",   "0", "#58A6FF")
        self.card_total    = StatCard("Total Scans",   "0", "#3FB950")
        self.card_last_uid = StatCard("Last UID",      "—", "#D2A8FF")
        self.card_last_uid.setFixedHeight(72)
        self.card_last_uid.value_label.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #D2A8FF; background: transparent; border: none; font-family: 'Consolas', monospace;"
        )

        row.addWidget(self.card_unique)
        row.addWidget(self.card_total)
        row.addWidget(self.card_last_uid, stretch=1)

        return row

    def _build_serial_group(self) -> QGroupBox:
        group = QGroupBox("Serial Connection")
        layout = QHBoxLayout(group)
        layout.setSpacing(10)

        port_label = QLabel("Port:")
        self.port_combo = QComboBox()

        self.refresh_ports_button = QPushButton("⟳  Refresh")
        self.refresh_ports_button.setObjectName("refreshBtn")
        self.refresh_ports_button.clicked.connect(self.load_ports)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setObjectName("connectBtn")
        self.connect_button.clicked.connect(self.connect_serial)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setObjectName("disconnectBtn")
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        self.disconnect_button.setEnabled(False)

        layout.addWidget(port_label)
        layout.addWidget(self.port_combo, stretch=1)
        layout.addWidget(self.refresh_ports_button)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)

        return group

    def _build_nav_group(self) -> QGroupBox:
        group = QGroupBox("Database Navigation")
        layout = QHBoxLayout(group)
        layout.setSpacing(10)

        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 14px; background: transparent; border: none;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Tag ID or RFID UID…")
        self.search_input.textChanged.connect(self.refresh_table)

        self.refresh_table_button = QPushButton("Refresh")
        self.refresh_table_button.setObjectName("refreshBtn")
        self.refresh_table_button.clicked.connect(self.refresh_table)

        self.clear_button = QPushButton("Clear Database")
        self.clear_button.setObjectName("clearBtn")
        self.clear_button.clicked.connect(self.clear_database)

        layout.addWidget(search_label)
        layout.addWidget(self.search_input, stretch=1)
        layout.addWidget(self.refresh_table_button)
        layout.addWidget(self.clear_button)

        return group

    def _build_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Tag ID", "RFID UID", "Scan Count", "First Seen", "Last Seen"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return table

    def _build_bottom_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        latest_group = QGroupBox("Latest Scan")
        latest_layout = QHBoxLayout(latest_group)
        self.latest_scan_label = QLabel("No tag scanned yet.")
        self.latest_scan_label.setStyleSheet(
            "font-family: 'Consolas', monospace; font-size: 13px; color: #58A6FF; background: transparent; border: none;"
        )
        latest_layout.addWidget(self.latest_scan_label)

        log_group = QGroupBox("Serial Log")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(130)
        log_layout.addWidget(self.log_output)

        row.addWidget(latest_group, stretch=1)
        row.addWidget(log_group, stretch=2)

        return row

    def load_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.port_combo.addItem("No ports found")
            self.connect_button.setEnabled(False)
            return
        for port in ports:
            self.port_combo.addItem(f"{port.device}  —  {port.description}", port.device)
        self.connect_button.setEnabled(True)

    def connect_serial(self):
        port_name = self.port_combo.currentData()
        if not port_name:
            QMessageBox.warning(self, "No Port", "Please select a valid serial port.")
            return

        self.serial_thread = SerialReaderThread(port_name)
        self.serial_thread.tag_scanned.connect(self.handle_tag_scanned)
        self.serial_thread.serial_message.connect(self.add_log)
        self.serial_thread.connection_error.connect(self.handle_serial_error)
        self.serial_thread.start()

        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.port_combo.setEnabled(False)
        self.status_badge.set_state("connected")

    def disconnect_serial(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.port_combo.setEnabled(True)
        self.status_badge.set_state("disconnected")

    def handle_tag_scanned(self, uid: str):
        result = self.db.add_or_update_tag(uid)
        self._total_scans += 1

        if result["status"] == "new":
            self._unique_tags += 1
            msg = f"NEW  {result['tag_id']}  |  UID: {result['rfid_uid']}  |  Count: {result['scan_count']}"
        else:
            msg = f"SEEN  {result['tag_id']}  |  UID: {result['rfid_uid']}  |  Count: {result['scan_count']}"

        self.latest_scan_label.setText(msg)
        self.card_last_uid.set_value(uid)
        self.card_total.set_value(str(self._total_scans))
        self.card_unique.set_value(str(self._unique_tags))

        self.add_log(msg)
        self.refresh_table()

    def refresh_table(self):
        search_text = self.search_input.text().strip()
        rows = self.db.get_all_tags(search_text)

        self.table.setRowCount(len(rows))

        mono_cols = {1}

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col_idx in mono_cols:
                    item.setFont(QFont("Consolas", 12))
                    item.setForeground(QColor("#D2A8FF"))
                elif col_idx == 0:
                    item.setForeground(QColor("#58A6FF"))
                elif col_idx == 2:
                    item.setForeground(QColor("#3FB950"))
                self.table.setItem(row_idx, col_idx, item)

        all_rows = self.db.get_all_tags()
        self._unique_tags = len(all_rows)
        self.card_unique.set_value(str(self._unique_tags))

    def clear_database(self):
        confirm = QMessageBox.question(
            self, "Clear Database",
            "Delete all saved RFID records?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.clear_database()
            self._total_scans = 0
            self._unique_tags = 0
            self.card_total.set_value("0")
            self.card_unique.set_value("0")
            self.card_last_uid.set_value("—")
            self.refresh_table()
            self.latest_scan_label.setText("Database cleared.")
            self.add_log("Database cleared.")

    def add_log(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"<span style='color:#484F58'>[{ts}]</span> {message}")

    def handle_serial_error(self, error_message: str):
        self.add_log(f"ERROR: {error_message}")
        self.status_badge.set_state("error")
        QMessageBox.critical(self, "Serial Error", error_message)
        self.disconnect_serial()

    def closeEvent(self, event):
        self.disconnect_serial()
        event.accept()




def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = RFIDDatabaseGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
