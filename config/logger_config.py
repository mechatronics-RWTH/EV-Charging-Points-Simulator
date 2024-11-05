# logger_config.py
import logging
from datetime import datetime
import sys
import os

logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

log_level = logging.INFO

def get_module_logger(module_name):
    # Create a custom logger
    logger = logging.getLogger(module_name)
    logger.propagate = False

    # Check if the directory exists and create it if necessary
    if not os.path.exists("OutputData/logs"):
        os.makedirs("OutputData/logs")
    
    # Create handlers
    f_handler = logging.FileHandler("OutputData/logs/main_trace.log")
    t_handler = logging.StreamHandler(sys.stdout)

    f_handler.setLevel(logging.ERROR)
    t_handler.setLevel(log_level)

    # Create formatters and add them to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    t_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    f_handler.setFormatter(f_format)
    t_handler.setFormatter(t_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    logger.addHandler(t_handler)

    return logger