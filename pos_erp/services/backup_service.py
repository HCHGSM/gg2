import os
import shutil
import sqlite3
from datetime import datetime
from pos_erp.database.db import DB_PATH

class BackupService:
    """
    خدمة النسخ الاحتياطي التلقائي واليدوي لقاعدة البيانات واستعادة النسخ السابقة.
    """
    @staticmethod
    def create_backup():
        try:
            backup_dir = os.path.expanduser('~/pos_backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"pos_backup_{timestamp}.db")
            
            with sqlite3.connect(DB_PATH) as src, sqlite3.connect(backup_path) as dst:
                src.backup(dst)
                
            return True, f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_path}", backup_path
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def restore_backup(backup_path):
        try:
            if not os.path.exists(backup_path):
                return False, "ملف النسخة الاحتياطية غير موجود"
            
            from pos_erp.database.db import engine, SessionLocal
            SessionLocal.remove()
            engine.dispose()
            
            wal_path = DB_PATH + "-wal"
            shm_path = DB_PATH + "-shm"
            if os.path.exists(wal_path): os.remove(wal_path)
            if os.path.exists(shm_path): os.remove(shm_path)
            
            shutil.copy2(backup_path, DB_PATH)
            return True, "تم استعادة النسخة الاحتياطية بنجاح"
        except Exception as e:
            return False, str(e)
