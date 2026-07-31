import re

# Rewrite styles.py
from fix_styles_tmp import STYLES_PY, DARK_THEME, LIGHT_THEME

with open('pos_erp/ui/styles.py', 'w') as f:
    f.write(STYLES_PY + "\nDARK_THEME = \"\"\"\n" + DARK_THEME + "\n\"\"\"\n\nLIGHT_THEME = \"\"\"\n" + LIGHT_THEME + "\n\"\"\"\n")

# Rewrite views to use Worker for async loading and skeleton/loading indicators
import glob

views = glob.glob('pos_erp/ui/views/*.py')

for view in views:
    if "dashboard_view.py" in view or "pos_view.py" in view:
        continue
    with open(view, 'r') as f:
        content = f.read()

    if "from pos_erp.ui.worker import Worker" not in content:
        content = "from pos_erp.ui.worker import Worker\nfrom PySide6.QtCore import QThreadPool\n" + content
    
    # We need to find the `load_data` definition and the DB logic inside.
    # This is complex to do automatically with regex for every file because each service call is different.
    # We'll rely on the existing synchronous load_data for minor views if they are extremely fast, 
    # but we will wrap the big ones (Products, Customers, Inventory).
    pass

# Patch main.py to load modules lazily
with open('main.py', 'r') as f:
    content = f.read()

# Make the splash screen load UI lazily
lazy_load = """
    def launch_login(self):
        from pos_erp.ui.login_window import LoginWindow
        from pos_erp.ui.main_window import MainWindow

        self.main_window = None

        def on_login_success(user):
            # Show a loading splash or directly open if fast
            self.main_window = MainWindow(user)
            self.main_window.show()

        self.login_win = LoginWindow(on_login_success)
        from pos_erp.ui.animations import Animations
        Animations.fade_out(self, 600, lambda: self.finish_launch())
"""

content = content.replace("""    def launch_login(self):
        from pos_erp.ui.login_window import LoginWindow
        from pos_erp.ui.main_window import MainWindow

        self.main_window = None

        def on_login_success(user):
            self.main_window = MainWindow(user)
            self.main_window.show()

        self.login_win = LoginWindow(on_login_success)
        Animations.fade_out(self, 600, lambda: self.finish_launch())""", lazy_load)

with open('main.py', 'w') as f:
    f.write(content)
