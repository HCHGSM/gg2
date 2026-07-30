# -*- coding: utf-8 -*-
"""
=============================================================================
Project: Enterprise ERP & POS Mega Suite
File: main_enterprise_app.py
Description: Main entry point for the professional desktop enterprise application.
=============================================================================
"""

from enterprise_pos_erp.database import init_db
from enterprise_pos_erp.gui import main

if __name__ == '__main__':
    print("=" * 70)
    print("جاري إطلاق نظام Enterprise ERP & POS المكتبي المتكامل...")
    print("=" * 70)
    main()
