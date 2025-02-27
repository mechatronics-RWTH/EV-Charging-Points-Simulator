import logging


def setup_logger(log_file_name: str, console_log_level: object = logging.DEBUG) -> logging.Logger:
    """

    :param log_file_name:
    :type log_file_name:
    :param console_log_level:
    :type console_log_level:
    :return:
    :rtype:
    """
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    logger = logging.getLogger('RlLibTraining')
    logger.setLevel(logging.DEBUG)


    fileHandler = logging.FileHandler(log_file_name)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(console_log_level)
    logger.addHandler(consoleHandler)

    logger.parent.setLevel(logging.WARNING)
    logger.propagate = False
    return logger
