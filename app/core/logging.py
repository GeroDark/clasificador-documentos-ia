import json
import logging
import sys


def setup_logging() -> None:
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def log_event(logger_name: str, **payload: object) -> None:
    logger = logging.getLogger(logger_name)
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))