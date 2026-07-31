import logging
import os
import sys


def _default_app_root():
    if getattr(sys, 'frozen', False):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return os.path.join(local_app_data, 'SmartPOS_ERP')
        return os.path.expanduser('~/.local/share/SmartPOS_ERP')
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Same reasoning as pos_erp/database/db.py: default to a location next to the
# app instead of silently writing to the user's home directory or a temp dir.
# Overridable via POS_ERP_LOG_PATH.
DEFAULT_LOG_PATH = os.path.join(_default_app_root(), 'data', 'pos_erp.log')
LOG_PATH = os.environ.get('POS_ERP_LOG_PATH', DEFAULT_LOG_PATH)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
