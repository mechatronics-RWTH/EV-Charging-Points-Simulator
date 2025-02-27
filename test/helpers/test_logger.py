from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

def test_logger():
    logger.info("Test logger")


if __name__ == "__main__":
    test_logger()