import os
import shutil
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
            shutil.copy2(DB_PATH, backup_path)
            return True, f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_path}"
        except Exception as e:
            return False, str(e)
