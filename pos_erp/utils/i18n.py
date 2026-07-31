import json

class I18n:
    _lang = "ar"
    
    _dict = {
        "ar": {
            "dashboard": "لوحة التحكم",
            "pos": "نقطة البيع (POS)",
            "products": "المنتجات",
            "inventory": "المخزون",
            "customers": "العملاء",
            "suppliers": "الموردين",
            "purchases": "المشتريات",
            "expenses": "المصروفات",
            "revenues": "الإيرادات",
            "accounts": "الحسابات",
            "reports": "التقارير",
            "settings": "الإعدادات",
            "users": "المستخدمين",
            "logout": "تسجيل الخروج",
            "about": "حول النظام",
            "theme": "تغيير المظهر",
            "lang": "English",
            "overview": "الرؤية الشاملة (Overview)",
            "total_sales": "إجمالي المبيعات",
            "total_purchases": "تكاليف التوريد",
            "net_profit": "صافي الأرباح",
            "low_stock": "تنبيهات المخزون",
            "recent_sales": "سجل المبيعات الأخيرة",
            "invoice_no": "رقم الفاتورة",
            "customer": "العميل",
            "total": "الإجمالي",
            "paid": "المدفوع",
            "status": "الحالة",
            "cash_client": "عميل نقدي",
            "search_ph": "🔍 البحث بالاسم أو الباركود...",
            "terminal": "نقطة البيع (Terminal)",
            "cart": "الفاتورة الحالية",
            "product": "المنتج",
            "price": "السعر",
            "qty": "الكمية",
            "subtotal": "المجموع الفرعي:",
            "tax": "الضريبة (15%):",
            "final_total": "الإجمالي النهائي:",
            "checkout": "إصدار الفاتورة ➔",
            "add": "➕ إضافة",
            "edit": "تعديل",
            "delete": "حذف",
            "save": "حفظ",
            "cancel": "إلغاء",
            "add_customer": "إضافة عميل جديد",
            "add_supplier": "إضافة مورد جديد",
            "add_product": "إضافة منتج تجاري جديد",
            "name": "الاسم:",
            "phone": "رقم الهاتف:",
            "email": "البريد الإلكتروني:",
            "address": "العنوان:",
            "tax_no": "الرقم الضريبي:",
            "app_title": "Smart ERP - Enterprise 2026"
        },
        "en": {
            "dashboard": "Dashboard",
            "pos": "Point of Sale (POS)",
            "products": "Products",
            "inventory": "Inventory",
            "customers": "Customers",
            "suppliers": "Suppliers",
            "purchases": "Purchases",
            "expenses": "Expenses",
            "revenues": "Revenues",
            "accounts": "Accounts",
            "reports": "Reports",
            "settings": "Settings",
            "users": "Users",
            "logout": "Logout",
            "about": "About System",
            "theme": "Toggle Theme",
            "lang": "العربية",
            "overview": "Executive Overview",
            "total_sales": "Total Sales",
            "total_purchases": "Supply Costs",
            "net_profit": "Net Profit",
            "low_stock": "Low Stock Alerts",
            "recent_sales": "Recent Sales History",
            "invoice_no": "Invoice No",
            "customer": "Customer",
            "total": "Total",
            "paid": "Paid",
            "status": "Status",
            "cash_client": "Walk-in Client",
            "search_ph": "🔍 Search by name or barcode...",
            "terminal": "POS Terminal",
            "cart": "Current Cart",
            "product": "Product",
            "price": "Price",
            "qty": "Qty",
            "subtotal": "Subtotal:",
            "tax": "Tax (15%):",
            "final_total": "Final Total:",
            "checkout": "Checkout ➔",
            "add": "➕ Add",
            "edit": "Edit",
            "delete": "Delete",
            "save": "Save",
            "cancel": "Cancel",
            "add_customer": "Add New Customer",
            "add_supplier": "Add New Supplier",
            "add_product": "Add New Product",
            "name": "Name:",
            "phone": "Phone:",
            "email": "Email:",
            "address": "Address:",
            "tax_no": "Tax Number:",
            "app_title": "Smart ERP - Enterprise 2026"
        }
    }

    @classmethod
    def set_language(cls, lang):
        if lang in cls._dict:
            cls._lang = lang

    @classmethod
    def toggle_language(cls):
        cls._lang = "en" if cls._lang == "ar" else "ar"
        return cls._lang

    @classmethod
    def t(cls, key, default=None):
        return cls._dict[cls._lang].get(key, default or key)

# Global helper alias
_ = I18n.t
