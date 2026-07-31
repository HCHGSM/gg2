from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QMessageBox
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Setting

class SettingsView(QWidget):
    """
    إعدادات النظام العامة، بيانات الشركة، الضرائب، والعملة.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        title = QLabel("إعدادات النظام والشركة التجارية")
        title.setProperty("cssClass", "view-title")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.company_name = QLineEdit()
        self.company_phone = QLineEdit()
        self.tax_rate = QLineEdit()

        form_layout.addRow("اسم المؤسسة / الشركة:", self.company_name)
        form_layout.addRow("رقم الهاتف الرسمي:", self.company_phone)
        form_layout.addRow("نسبة الضريبة الأساسية (%):", self.tax_rate)

        layout.addLayout(form_layout)

        save_btn = QPushButton("💾 حفظ الإعدادات")
        save_btn.setProperty("cssClass", "primary")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.load_settings()

    def load_settings(self):
        session = SessionLocal()
        try:
            c_name = session.query(Setting).filter_by(key='company_name').first()
            c_phone = session.query(Setting).filter_by(key='company_phone').first()
            t_rate = session.query(Setting).filter_by(key='tax_rate').first()

            if c_name: self.company_name.setText(c_name.value)
            if c_phone: self.company_phone.setText(c_phone.value)
            if t_rate: self.tax_rate.setText(t_rate.value)
        finally:
            session.close()

    def save_settings(self):
        session = SessionLocal()
        try:
            settings_map = {
                'company_name': self.company_name.text().strip(),
                'company_phone': self.company_phone.text().strip(),
                'tax_rate': self.tax_rate.text().strip()
            }
            for k, v in settings_map.items():
                s = session.query(Setting).filter_by(key=k).first()
                if s:
                    s.value = v
                else:
                    session.add(Setting(key=k, value=v))
            session.commit()
            QMessageBox.information(self, "نجاح", "تم حفظ إعدادات النظام بنجاح")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", str(e))
        finally:
            session.close()
