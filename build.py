import subprocess
import sys
import os

def build_executable():
    print("=" * 60)
    print("جاري بناء ملف البرنامج التنفيذي (Executable) باستخدام PyInstaller...")
    print("=" * 60)
    
    cmd = [sys.executable, "-m", "PyInstaller", "SmartPOS.spec", "--clean"]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("تم بناء البرنامج بنجاح!")
        print("الملف التنفيذي جاهز في مجلد: dist/SmartPOS_ERP")
        print("=" * 60)
    else:
        print("\nحدث خطأ أثناء بناء البرنامج.")

if __name__ == '__main__':
    build_executable()
