import os
import sys
import traceback
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar, QMessageBox, QFrame
from pos_erp.utils.logger import log_error
from pos_erp.ui.animations import Animations

def _resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def global_exception_handler(exctype, value, tb):
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    log_error(f"CRASH: {error_msg}")
    if QApplication.instance():
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("System Crash (Fatal Error)")
        msg_box.setText("حدث خطأ غير متوقع في النظام.")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()
    sys.exit(1)

sys.excepthook = global_exception_handler

class InitThread(QThread):
    finished_init = Signal()
    error_init = Signal(str)
    
    def run(self):
        try:
            from pos_erp.database.db import init_db
            init_db()
            self.finished_init.emit()
        except Exception as e:
            self.error_init.emit(str(e))

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(640, 420)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.card = QFrame()
        self.card.setStyleSheet("background-color: rgba(9, 9, 11, 0.95); border: 1px solid #27272A; border-radius: 30px;")
        self.card.setFixedSize(540, 320)
        Animations.apply_glow(self.card, "#6366F1", 80, 120)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(25)
        
        logo = QLabel("✧")
        logo.setStyleSheet("font-size: 80px; color: #6366F1; font-weight: 900; background: transparent; border: none;")
        logo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(logo)
        
        title = QLabel("SMART ERP 2026")
        title.setStyleSheet("font-size: 34px; font-weight: 900; color: white; letter-spacing: 4px; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        self.lbl_status = QLabel("جاري تهيئة خوادم النظام (Initializing Engine)...")
        self.lbl_status.setStyleSheet("color: #A1A1AA; font-size: 16px; background: transparent; border: none; letter-spacing: 1px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_status)
        
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("QProgressBar { background: #27272A; border: none; border-radius: 4px; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #10B981); border-radius: 4px; }")
        self.progress.setValue(0)
        card_layout.addWidget(self.progress)
        
        layout.addWidget(self.card)
        
        Animations.fade_in(self, 1200)
        Animations.pop_in(self.card, 1500)
        
        self.thread = InitThread()
        self.thread.finished_init.connect(self.on_init_success)
        self.thread.error_init.connect(self.on_init_error)
        
        self.prog_val = 0
        self.prog_timer = QTimer()
        self.prog_timer.timeout.connect(self.update_progress)
        self.prog_timer.start(25)
        
        self.thread.start()

    def update_progress(self):
        if self.prog_val < 90:
            self.prog_val += 1
            self.progress.setValue(self.prog_val)

    def on_init_success(self):
        self.progress.setValue(100)
        self.lbl_status.setText("تم التوصيل بنجاح. جاري فتح النظام...")
        self.lbl_status.setStyleSheet("color: #10B981; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        QTimer.singleShot(1000, self.launch_login)
        
    def on_init_error(self, err):
        self.lbl_status.setText(f"خطأ: {err}")
        self.lbl_status.setStyleSheet("color: #EF4444; font-size: 15px; background: transparent;")

    def launch_login(self):
        from pos_erp.ui.login_window import LoginWindow
        from pos_erp.ui.main_window import MainWindow

        self.main_window = None

        def on_login_success(user):
            self.main_window = MainWindow(user)
            self.main_window.show()

        self.login_win = LoginWindow(on_login_success)
        Animations.fade_out(self, 800, lambda: self.finish_launch())
        
    def finish_launch(self):
        self.login_win.show()
        self.close()

def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    icon_path = _resource_path(os.path.join('assets', 'icons', 'app_icon.ico'))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    splash = SplashScreen()
    splash.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
