# -*- coding: utf-8 -*-
"""
=============================================================================
Project: Ultra-Advanced Enterprise POS & ERP System
File: pos_erp/utils/helpers.py
Description: General formatting, currency conversion, date utilities, and validation helpers.
=============================================================================
"""

def format_currency(amount, currency_symbol="ج.س"):
    """Format numeric float amount into standard commercial currency string."""
    try:
        return f"{float(amount):,.2f} {currency_symbol}"
    except (ValueError, TypeError):
        return f"0.00 {currency_symbol}"

def validate_phone(phone_str):
    """Validate phone number format."""
    if not phone_str:
        return True # Optional
    cleaned = ''.join(filter(str.isdigit, phone_str))
    return len(cleaned) >= 7

def sanitize_input(text):
    """Sanitize text input against basic injection vulnerabilities."""
    if not text:
        return ""
    return str(text).strip().replace("'", "").replace(";", "")
