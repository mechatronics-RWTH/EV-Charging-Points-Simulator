# logger_config.py
import logging
from datetime import datetime
import sys
import os

# logging.getLogger('PIL').setLevel(logging.WARNING)
# logging.getLogger('matplotlib').setLevel(logging.WARNING)
from datetime import datetime

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
FILE_NAME = f"OutputData/logs/main_trace_{current_datetime}.log"

log_level_terminal = logging.INFO
log_level_file = logging.INFO

def get_module_logger(module_name):
    # Create a custom logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)  # Set the logger level to DEBUG
    logger.propagate = False

    # Check if the directory exists and create it if necessary
    #if not os.path.exists("OutputData/logs"):
    os.makedirs("OutputData/logs", exist_ok=True)
    
    # Create handlers
    f_handler = logging.FileHandler(FILE_NAME)
    t_handler = logging.StreamHandler(sys.stdout)

    f_handler.setLevel(log_level_file)
    t_handler.setLevel(log_level_terminal)

    # Create formatters and add them to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    t_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    f_handler.setFormatter(f_format)
    t_handler.setFormatter(t_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    logger.addHandler(t_handler)
    level = logger.getEffectiveLevel()
    level_name = logging.getLevelName(level)
    return logger