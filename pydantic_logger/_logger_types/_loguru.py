from typing import Protocol
from typing import runtime_checkable

from loguru import logger as _loguru_default_logger
from loguru._logger import Logger

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    def bind(self, **kwargs: object) -> "_Logger": ...


if not issubclass(Logger, _Logger):
    raise ValueError(
        f"{Logger.__name__} is not an subclass of {_Logger.__name__}"
    )


class _PydanticLoguruLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        return _loguru_default_logger.bind(name=self.name)
