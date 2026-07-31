import re

with open('pos_erp/ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded sizing with maximized responsive layout
old_init = """    def init_ui(self):
        self.setWindowTitle("Smart ERP - Enterprise 2026")
        self.resize(1600, 900)
        self.setStyleSheet(DARK_THEME)"""

new_init = """    def init_ui(self):
        self.setWindowTitle("Smart ERP - Enterprise 2026")
        
        # Responsive Sizing (Launch maximized or 80% of screen)
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.85)
        height = int(screen.height() * 0.85)
        self.resize(width, height)
        
        # We start dark or light based on preferences, letting default be LIGHT to match Claude style user requested
        self.dark_mode = False
        self.setStyleSheet(LIGHT_THEME)"""

if "self.resize(1600, 900)" in content:
    content = content.replace(old_init, new_init)

# Fix translations and add a toggle button for language. But wait, I'll add language toggle directly in Header.
if "theme_btn.clicked.connect(self.toggle_theme)" in content and "lang_btn" not in content:
    old_theme_block = """        theme_btn = QPushButton("🌓")
        theme_btn.setFixedSize(50, 50)
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setStyleSheet("font-size: 22px; border: none; background: transparent; border-radius: 25px;")
        theme_btn.setToolTip("تغيير المظهر")
        theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_btn)"""

    new_theme_block = """        # Language Toggle
        self.lang_btn = QPushButton("EN")
        self.lang_btn.setFixedSize(50, 50)
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.setStyleSheet("font-size: 16px; font-weight: bold; border: none; background: transparent; border-radius: 25px;")
        self.lang_btn.setToolTip("تغيير اللغة (Change Language)")
        from pos_erp.utils.i18n import I18n
        self.lang_btn.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.lang_btn)
        
        theme_btn = QPushButton("🌓")
        theme_btn.setFixedSize(50, 50)
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setStyleSheet("font-size: 22px; border: none; background: transparent; border-radius: 25px;")
        theme_btn.setToolTip("تغيير المظهر")
        theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_btn)"""

    content = content.replace(old_theme_block, new_theme_block)

    # Add the missing method
    if "def toggle_language" not in content:
        content += """
    def toggle_language(self):
        from pos_erp.utils.i18n import I18n
        new_lang = I18n.toggle_language()
        self.lang_btn.setText("AR" if new_lang == "en" else "EN")
        # In a real app we'd trigger a reload here. Since we are patching live,
        # we restart the UI by effectively logging out silently or showing a toast
        from pos_erp.ui.animations import ToastManager
        ToastManager.show_info(self, "Language changed. Restart window to apply fully.")
        """

with open('pos_erp/ui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)
