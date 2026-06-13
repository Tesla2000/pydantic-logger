import logging
import os
from logging import Logger
from typing import Protocol
from typing import runtime_checkable
from typing import Union

from pydantic import Field
from pydantic import PositiveInt

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase

if not issubclass(Logger, _LoggerProtocol):
    raise ValueError(
        f"{Logger.__name__} is not an subclass of {_LoggerProtocol.__name__}"
    )


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    def log(
        self, level: int, msg: str, *args: object, **kwargs: object
    ) -> object: ...


def _get_stack_level() -> Union[int, None]:
    stack_level = os.getenv("PYDANTIC_LOGGER_STACK_LEVEL")
    if stack_level is None:
        return stack_level
    level = int(stack_level)
    if level < 1:
        raise ValueError(
            f"{stack_level=} must be None of {PositiveInt.__name__}"
        )
    return int(stack_level)


class _PydanticBuiltinLogger(_PydanticLoggerBase[_Logger]):
    stack_level: Union[PositiveInt, None] = Field(
        default_factory=_get_stack_level,
    )

    def _create_logger(self) -> _Logger:
        logger = logging.getLogger(self.name)
        if self.level is not None:
            logger.setLevel(self.level)
        assert isinstance(logger, _Logger)
        return logger

    def _set_stack_level_if_configured(
        self, kwargs: dict[str, object]
    ) -> None:
        if self.stack_level is None:
            return
        kwargs.setdefault("stack_level", self.stack_level)

    def log(
        self, level: int, msg: str, *args: object, **kwargs: object
    ) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.log(level, msg, *args, **kwargs)
