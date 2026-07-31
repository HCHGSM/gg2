import platform
import subprocess
import sys
import os


def build_executable():
    print("=" * 60)
    print("جاري بناء ملف البرنامج التنفيذي (Executable) باستخدام PyInstaller...")
    print("=" * 60)

    if platform.system() != "Windows":
        print(
            "\n[تحذير] PyInstaller لا يقوم بالبناء المتقاطع (cross-compile).\n"
            "لإنتاج ملف .exe يعمل على Windows، يجب تشغيل هذا السكربت على\n"
            "جهاز Windows فعلي (أو صورة Windows CI)، وليس على Linux/macOS.\n"
            "سيتابع البناء الآن وينتج ملفاً تنفيذياً لهذا النظام الحالي فقط.\n"
        )

    cmd = [sys.executable, "-m", "PyInstaller", "SmartPOS.spec", "--clean"]
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("تم بناء البرنامج بنجاح!")
        print("الملف التنفيذي جاهز في مجلد: dist/SmartPOS_ERP" + (".exe" if platform.system() == "Windows" else ""))
        print("=" * 60)
    else:
        print("\nحدث خطأ أثناء بناء البرنامج. راجع الرسائل أعلاه لتفاصيل الخطأ.")
        sys.exit(result.returncode)


if __name__ == '__main__':
    build_executable()
