import re

# Patch Customers View
with open('pos_erp/ui/views/customers_view.py', 'r') as f:
    content = f.read()

imports = """from pos_erp.ui.dialogs import CustomerForm
from pos_erp.services.crm_service import CRMService
from pos_erp.ui.animations import ToastManager
from pos_erp.ui.worker import Worker
from PySide6.QtCore import QThreadPool"""

if "CustomerForm" not in content:
    content = imports + "\n" + content

content = re.sub(r'add_btn\.clicked\.connect\(lambda: QMessageBox\.information.*?$', 'add_btn.clicked.connect(self.show_add_dialog)', content, flags=re.MULTILINE)

new_methods = """
    def show_add_dialog(self):
        dialog = CustomerForm(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                ToastManager.show_error(self.window(), "اسم العميل مطلوب")
                return
            success, msg = CRMService.add_customer(data)
            if success:
                ToastManager.show_success(self.window(), msg)
                self.load_data()
            else:
                ToastManager.show_error(self.window(), msg)
"""
if "def show_add_dialog(self):" not in content:
    content += new_methods

with open('pos_erp/ui/views/customers_view.py', 'w') as f:
    f.write(content)


# Patch Suppliers View
with open('pos_erp/ui/views/suppliers_view.py', 'r') as f:
    content = f.read()

imports = """from pos_erp.ui.dialogs import SupplierForm
from pos_erp.services.crm_service import CRMService
from pos_erp.ui.animations import ToastManager
from pos_erp.ui.worker import Worker
from PySide6.QtCore import QThreadPool"""

if "SupplierForm" not in content:
    content = imports + "\n" + content

content = re.sub(r'add_btn\.clicked\.connect\(lambda: QMessageBox\.information.*?$', 'add_btn.clicked.connect(self.show_add_dialog)', content, flags=re.MULTILINE)

new_methods = """
    def show_add_dialog(self):
        dialog = SupplierForm(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                ToastManager.show_error(self.window(), "اسم المورد مطلوب")
                return
            success, msg = CRMService.add_supplier(data)
            if success:
                ToastManager.show_success(self.window(), msg)
                self.load_data()
            else:
                ToastManager.show_error(self.window(), msg)
"""
if "def show_add_dialog(self):" not in content:
    content += new_methods

with open('pos_erp/ui/views/suppliers_view.py', 'w') as f:
    f.write(content)
