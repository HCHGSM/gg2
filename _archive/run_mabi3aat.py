import uvicorn
from mabi3aat_mega.core.database import init_mabi3aat_db

if __name__ == '__main__':
    print("=" * 70)
    print("جاري إطلاق نظام (مبيعات دوت كوم الإمبراطوري) المتكامل...")
    print("رابط النظام المحلي: http://127.0.0.1:8090")
    print("بيانات الدخول: admin / admin123")
    print("=" * 70)
    init_mabi3aat_db()
    uvicorn.run("mabi3aat_mega.web.app:app", host="127.0.0.1", port=8090, reload=False)
