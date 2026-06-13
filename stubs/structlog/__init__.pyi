from typing import Any

from structlog._config import BoundLoggerLazyProxy


def get_logger(*args: Any, **initial_values: Any) -> BoundLoggerLazyProxy: ...
