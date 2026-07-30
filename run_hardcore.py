# -*- coding: utf-8 -*-
"""
=============================================================================
Project: Hardcore Enterprise ERP & POS
File: run_hardcore.py
Description: Entry point for the strict, mathematically sound enterprise application.
=============================================================================
"""

from hardcore_erp.core.database import init_hardcore_db
from hardcore_erp.ui.gui import main

if __name__ == '__main__':
    print("=" * 70)
    print("جاري تشغيل نظام Hardcore Enterprise ERP & POS ذو الحسابات الدقيقة...")
    print("=" * 70)
    main()
