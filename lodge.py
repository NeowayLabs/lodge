import os
import json
import sys
import logging


# To be used by tests
DEFAULT_LOG_STREAM = sys.stderr


def _get_log_level_from_env_var(logger_name: str) -> str:
    DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    uppercase_underline = "_".join(logger_name.split(".")).upper()
    env_var_key = f"{uppercase_underline}_LOG_LEVEL"
    return os.environ.get(env_var_key, DEFAULT_LOG_LEVEL)


def _get_format():
    DEFAULT_LOG_ENV = os.environ.get("LOG_ENV", "PROD")
    BASE_STRUCTURED = {
        "message": "%(message)s",
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
    }

    if DEFAULT_LOG_ENV == "PROD":
        log_format = json.dumps(BASE_STRUCTURED)
    else:
        log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    return logging.Formatter(log_format)


def _add_base_configs(logger: logging.Logger):
    logging.addLevelName(logging.CRITICAL, "FATAL")
    logging.addLevelName(logging.WARNING, "WARN")


def _add_handlers(logger: logging.Logger):
    stderr = logging.StreamHandler(DEFAULT_LOG_STREAM)
    stderr.setFormatter(_get_format())
    logger.addHandler(stderr)


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with configs based on the environment.

    You're not encouraged to use this function, you should use `log` or
    `logger` directly
    """
    logger = logging.getLogger(name)

    _add_base_configs(logger)
    _add_handlers(logger)

    logger.setLevel(_get_log_level_from_env_var(name))
    return logger
