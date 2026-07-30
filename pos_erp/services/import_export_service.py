import csv
import os

class ImportExportService:
    """
    خدمة استيراد وتصدير بيانات المنتجات والعملاء عبر ملفات CSV و Excel.
    """
    @staticmethod
    def export_csv(file_path, headers, rows):
        try:
            with open(file_path, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            return True, "تم تصدير البيانات بنجاح"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def import_csv(file_path):
        try:
            data = []
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
                for row in reader:
                    data.append(row)
            return True, data, "تم استيراد البيانات بنجاح"
        except Exception as e:
            return False, [], str(e)
