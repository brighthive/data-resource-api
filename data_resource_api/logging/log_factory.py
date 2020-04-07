"""Log Factory."""

import logging


class LogFactory:
    """Log Factory Class."""

    @staticmethod
    def get_console_logger(logger_name: str = ""):
        """Return a simple console logger."""

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_logger = logging.StreamHandler()
        console_logger.setLevel(logging.INFO)
        console_logger.setFormatter(log_formatter)
        logger.addHandler(console_logger)
        return logger
