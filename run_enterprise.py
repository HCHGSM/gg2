import uvicorn
from enterprise_erp.core.engine import init_enterprise_db

if __name__ == '__main__':
    print("=" * 70)
    print("جاري تشغيل أضخم نظام ERP و POS تجاري في العالم (Enterprise Mega Suite)...")
    print("رابط النظام المحلي: http://127.0.0.1:8080")
    print("بيانات الدخول: admin / admin123")
    print("=" * 70)
    init_enterprise_db()
    uvicorn.run("enterprise_erp.api.server:app", host="127.0.0.1", port=8080, reload=False)
