import logging
import os

LOG_PATH = os.path.expanduser('~/pos_erp.log')

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
