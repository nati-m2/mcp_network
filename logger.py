import logging
import colorlog

def get_logger(name: str = "MCP") -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:  # מוסיף handler רק אם אין כבר
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            }
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger
