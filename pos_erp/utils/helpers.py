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

# NOTE: no manual "sanitize_input" helper here on purpose. SQL injection
# protection already comes from SQLAlchemy's parameterized queries (used
# throughout pos_erp/services/*) — a blacklist-based string sanitizer would
# both fail to add real protection and corrupt legitimate input (e.g. an
# apostrophe in a customer name like "O'Brien").
