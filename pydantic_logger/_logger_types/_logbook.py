from typing import Protocol
from typing import runtime_checkable

import logbook

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    level: int


if not issubclass(logbook.Logger, _LoggerProtocol):
    raise ValueError(
        f"{logbook.Logger.__name__} is not an subclass of {_LoggerProtocol.__name__}"
    )


class _PydanticLogbookLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        logger = logbook.Logger(self.name)
        if self.level is not None:
            logger.level = (
                logbook.lookup_level(self.level)
                if isinstance(self.level, str)
                else self.level
            )
        return logger
