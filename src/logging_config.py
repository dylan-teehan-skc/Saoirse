import logging

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class NoColorFormatter(logging.Formatter):
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    
    def format(self, record):
        formatter = logging.Formatter(self.format_str)
        return formatter.format(record)

def setup_logging():
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter())

    # Create file handler with a lower log level
    fh = logging.FileHandler("debug.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(NoColorFormatter())

    # Add the handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger