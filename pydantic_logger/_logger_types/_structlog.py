from typing import Any
from typing import cast
from typing import Protocol
from typing import runtime_checkable

import structlog
from structlog.stdlib import BoundLogger

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    def bind(self, **kwargs: Any) -> "_Logger": ...


if not issubclass(BoundLogger, _Logger):
    raise ValueError(
        f"{BoundLogger.__name__} is not an subclass of {_Logger.__name__}"
    )


class _PydanticStructlogLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        return cast(_Logger, structlog.get_logger(self.name))
