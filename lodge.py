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


def _get_default_format():
    DEFAULT_LOG_ENV = os.environ.get("LOG_ENV", "PROD")
    LOG_BASE_FIELDS = eval(
        os.environ.get(
            "LOG_BASE_FIELDS",
            '{"message":"%(message)s","timestamp":"%(asctime)s","level":"%(levelname)s",}'
        )
    )
    LOG_EXTRA_FIELDS = eval(os.environ.get("LOG_EXTRA_FIELDS", '{}'))

    if DEFAULT_LOG_ENV == "PROD":
        log_format = json.dumps({**LOG_BASE_FIELDS, **LOG_EXTRA_FIELDS})
    else:
        log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    return logging.Formatter(log_format)


def _add_base_configs(logger: logging.Logger):
    logging.addLevelName(logging.CRITICAL, "FATAL")
    logging.addLevelName(logging.WARNING, "WARN")


def _add_default_handler(logger: logging.Logger):
    stderr = logging.StreamHandler(DEFAULT_LOG_STREAM)
    stderr.setFormatter(_get_default_format())
    logger.addHandler(stderr)


# https://github.com/python/cpython/blob/e8e341993e3f80a3c456fb8e0219530c93c13151/Lib/logging/__init__.py#L162
if hasattr(sys, '_getframe'):
    currentframe = lambda level: sys._getframe(level)  # noqa
else:  # pragma: no cover
    def currentframe(level: int):
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back  # type: ignore


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with configs based on the environment.

    You're not encouraged to use this function, you should use `log` or
    `logger` directly
    """
    logger = logging.getLogger(name)

    _add_base_configs(logger)
    _add_default_handler(logger)

    logger.setLevel(_get_log_level_from_env_var(name))
    return logger


class _ProxyLogger:
    """
    Internal proxy Logger Class. It should not be used directly. Use `log`
    or `logger`!

    From the proxy methods it will select the proper log to call.  If it
    not exists it will create a new one based on the callers `__name__`.
    The created logger will have the config loaded from the env vars.
    """
    def __init__(self):
        self.manager = logging.root.manager

    def _get_or_create_logger(self, name: str) -> logging.Logger:
        logger_already_initialized = name in self.manager.loggerDict.keys()
        if logger_already_initialized:
            return logging.getLogger(name)
        else:
            return get_logger(name)

    def _get_caller_module(self) -> str:
        # Calling currentframe from here we need to go 4 levels deep to reach the module
        # By changing currentframe call location this number will probably change.
        STACK_LEVEL = 4
        frame = currentframe(STACK_LEVEL)
        return frame.f_globals["__name__"]

    def _get_logger(self) -> logging.Logger:
        caller_name = self._get_caller_module()
        logger = self._get_or_create_logger(caller_name)
        return logger

    # Proxy methods
    def debug(self, msg, *args, **kwargs):
        self._get_logger().debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._get_logger().info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._get_logger().warn(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._get_logger().error(msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self._get_logger().fatal(msg, *args, **kwargs)


logger = _ProxyLogger()
# If you prefer `log` instead of `logger`
log = logger
