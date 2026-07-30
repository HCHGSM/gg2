import uvicorn
from pos_erp.database.db import init_db

if __name__ == "__main__":
    print("=" * 60)
    print("جاري تشغيل تطبيق الويب (Smart POS & ERP Web Application)...")
    print("رابط النظام المحلي: http://127.0.0.1:8000")
    print("بيانات الدخول الافتراضية: admin / admin123")
    print("=" * 60)
    init_db()
    uvicorn.run("web_app.app:app", host="127.0.0.1", port=8000, reload=False)
