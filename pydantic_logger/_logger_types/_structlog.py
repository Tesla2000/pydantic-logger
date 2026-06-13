from typing import Protocol
from typing import runtime_checkable

import structlog
from structlog.stdlib import BoundLogger

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase

if not issubclass(BoundLogger, _LoggerProtocol):
    raise ValueError(
        f"{BoundLogger.__name__} is not an subclass of {_LoggerProtocol.__name__}"
    )


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    def bind(self, **kwargs: object) -> "_Logger": ...


class _PydanticStructlogLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        logger = structlog.get_logger(self.name)
        assert isinstance(logger, _Logger)
        return logger
