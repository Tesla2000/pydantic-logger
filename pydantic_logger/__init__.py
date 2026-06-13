from typing import TYPE_CHECKING

from pydantic_logger import _logger_types
from pydantic_logger._logging_config import (
    _FileHandlerConfig as FileHandlerConfig,
)
from pydantic_logger._logging_config import _LoggingConfig as LoggingConfig
from pydantic_logger._logging_config import (
    _StreamHandlerConfig as StreamHandlerConfig,
)
from pydantic_logger._logging_level import _LoggingLevel as LoggingLevel
from pydantic_logger._logging_level import (
    _LoggingLevelAnnotation as LoggingLevelAnnotation,
)
from pydantic_logger._pydantic_logger_base import (
    _PydanticLoggerBase as PydanticLoggerBase,
)

if TYPE_CHECKING:
    PydanticEliotLogger = _logger_types.PydanticEliotLogger
    PydanticLogbookLogger = _logger_types.PydanticLogbookLogger
    PydanticLogfireLogger = _logger_types.PydanticLogfireLogger
    PydanticLoguruLogger = _logger_types.PydanticLoguruLogger
    PydanticPicologgingLogger = _logger_types.PydanticPicologgingLogger
    PydanticStructlogLogger = _logger_types.PydanticStructlogLogger


PydanticLogger = PydanticBuiltinLogger = _logger_types.PydanticBuiltinLogger

__all__ = [
    "PydanticLogger",
    "PydanticBuiltinLogger",
    "PydanticLoggerBase",
    "LoggingConfig",
    "StreamHandlerConfig",
    "FileHandlerConfig",
    "LoggingLevel",
    "LoggingLevelAnnotation",
    "PydanticLoguruLogger",
    "PydanticStructlogLogger",
    "PydanticLogbookLogger",
    "PydanticPicologgingLogger",
    "PydanticEliotLogger",
    "PydanticLogfireLogger",
]

_OPTIONAL_LOGGERS = {
    "PydanticLoguruLogger",
    "PydanticStructlogLogger",
    "PydanticLogbookLogger",
    "PydanticPicologgingLogger",
    "PydanticEliotLogger",
    "PydanticLogfireLogger",
}


def __getattr__(name: str) -> object:
    if name in _OPTIONAL_LOGGERS:
        return getattr(_logger_types, name)  # ignore
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
