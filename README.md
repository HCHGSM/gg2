# نظام المبيعات ونقاط البيع المتكامل (Smart POS & ERP - Desktop & Web)

برنامج مبيعات ونقاط بيع ومخازن تجاري احترافي، مصمم للعمل كـ **برنامج سطح مكتب (Desktop App)** عبر PySide6 أو كـ **تطبيق ويب** عبر FastAPI.

> ℹ️ هذا المشروع يحتوي على نسخة واحدة نشطة فقط من التطبيق: `pos_erp/` (سطح المكتب) + `web_app/` (الويب)، يتشاركان نفس قاعدة البيانات. أي مجلدات أخرى قد تجدها داخل `_archive/` هي محاولات سابقة مهجورة تم أرشفتها ولا يتم صيانتها.

---

## 🎨 الواجهات وتصميم (UI/UX)
- تصميم عصري، دعم كامل للغة العربية (RTL).
- واجهة سطح مكتب (PySide6) وواجهة ويب (FastAPI + Jinja2) تعملان على نفس قاعدة البيانات.

---

## 🚀 التشغيل من المصدر (Development)

```bash
python -m venv .venv
source .venv/bin/activate        # على ويندوز: .venv\Scripts\activate
pip install -r requirements.txt
```

**تطبيق سطح المكتب:**
```bash
python main.py
```

**تطبيق الويب:**
```bash
python run_web.py
```
ثم افتح المتصفح على: `http://127.0.0.1:8000`

**تشغيل الاختبارات:**
```bash
pytest tests/ -v
```

---

## 🔑 بيانات تسجيل الدخول الافتراضية

* **اسم المستخدم:** `admin`
* **كلمة المرور:** `admin123`

⚠️ **يجب تغيير كلمة المرور فوراً بعد أول تسجيل دخول.** يمكن أيضاً تعيين كلمة مرور مختلفة عند أول تشغيل عبر متغير البيئة:
```bash
export POS_ERP_ADMIN_PASSWORD="your-strong-password"   # قبل أول تشغيل فقط (قبل إنشاء قاعدة البيانات)
```

---

## ⚙️ متغيرات البيئة (Environment Variables)

| المتغير | الوصف | الافتراضي |
|---|---|---|
| `POS_ERP_DB_PATH` | مسار ملف قاعدة البيانات | `./data/pos_erp.db` (أو `%LOCALAPPDATA%\SmartPOS_ERP\data\pos_erp.db` عند التشغيل كملف exe مجمّع) |
| `POS_ERP_LOG_PATH` | مسار ملف السجلات | نفس منطق `POS_ERP_DB_PATH` أعلاه |
| `POS_ERP_ADMIN_PASSWORD` | كلمة مرور المدير الافتراضية عند أول تشغيل فقط | `admin123` |
| `POS_ERP_SESSION_TTL` | مدة صلاحية جلسة الويب بالثواني | `28800` (8 ساعات) |
| `POS_ERP_ENV` | اضبطها على `production` عند التشغيل خلف HTTPS لتفعيل خاصية `secure` لملفات تعريف الارتباط | `development` |

---

## 📁 هيكل المشروع

```
pos_erp/            # النواة المشتركة: قاعدة البيانات، الخدمات، واجهة سطح المكتب
web_app/             # تطبيق الويب (FastAPI) + القوالب
main.py              # نقطة تشغيل سطح المكتب
run_web.py           # نقطة تشغيل الويب
tests/               # اختبارات الوحدة
assets/icons/        # أيقونة التطبيق (لتغليف Windows)
SmartPOS.spec        # ملف PyInstaller لبناء ملف exe
version_info.txt     # معلومات إصدار ويندوز المضمّنة في exe
installer/           # سكربت Inno Setup لبناء المثبّت
docs/                # التوثيق (المعمارية، دليل المستخدم، API، النشر، البناء)
_archive/            # محاولات سابقة مهجورة (غير مُصانة)
```

---

## 📦 بناء نسخة Windows التنفيذية (exe) والمثبّت

راجع [`docs/build_instructions.md`](docs/build_instructions.md) للتفاصيل الكاملة. **ملاحظة مهمة: يجب تنفيذ خطوات البناء هذه على جهاز Windows فعلي** — لا يمكن لأداة PyInstaller بناء ملف exe يعمل على Windows من داخل بيئة Linux/macOS.

---

## 📚 توثيق إضافي

- [`docs/architecture.md`](docs/architecture.md) — نظرة على البنية المعمارية
- [`docs/user_guide.md`](docs/user_guide.md) — دليل المستخدم
- [`docs/api.md`](docs/api.md) — مرجع الخدمات الداخلية
- [`docs/deployment_guide.md`](docs/deployment_guide.md) — دليل النشر (سطح مكتب وويب)
- [`docs/build_instructions.md`](docs/build_instructions.md) — بناء exe والمثبّت لويندوز
- [`docs/testing_checklist.md`](docs/testing_checklist.md) — قائمة التحقق قبل الإصدار
- [`CHANGELOG.md`](CHANGELOG.md) — سجل التغييرات
- [`AUDIT_REPORT.md`](AUDIT_REPORT.md) / [`FINAL_AUDIT_REPORT.md`](FINAL_AUDIT_REPORT.md) — تقارير التدقيق
