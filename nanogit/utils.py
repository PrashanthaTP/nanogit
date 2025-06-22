import logging

LOGGER_NAME = "nano-git"
LOGGER_FORMAT = "%(asctime)s | (%(levelname)s) %(name)s - %(message)s"
LOGGER_DATEFORMAT = "%d-%m-%Y %H:%M:%S"
logging.basicConfig(level=logging.INFO,
                    format=LOGGER_FORMAT,
                    datefmt=LOGGER_DATEFORMAT)

def get_logger():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(fmt=LOGGER_FORMAT, datefmt=LOGGER_DATEFORMAT)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    return logger
