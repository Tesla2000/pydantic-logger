from typing import Protocol
from typing import runtime_checkable

from loguru import logger as _loguru_default_logger
from loguru._logger import Logger as LoguruLogger

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase

if not issubclass(LoguruLogger, _LoggerProtocol):
    raise ValueError(
        f"{LoguruLogger.__name__} is not an subclass of {_LoggerProtocol.__name__}"
    )


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    def bind(self, **kwargs: object) -> "_Logger": ...


class _PydanticLoguruLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        logger = _loguru_default_logger.bind(name=self.name)
        assert isinstance(logger, _Logger)
        return logger
