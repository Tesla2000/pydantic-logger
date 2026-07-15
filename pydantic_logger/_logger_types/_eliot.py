import sys
from typing import TYPE_CHECKING

_ELIOT_MIN_PYTHON = (3, 10)

if sys.version_info[:2] >= _ELIOT_MIN_PYTHON:
    from typing import ClassVar, Protocol, runtime_checkable

    from eliot import log_message
    from pydantic import BaseModel, ConfigDict

    from pydantic_logger._logger_protocol import _LoggerProtocol
    from pydantic_logger._pydantic_logger_base import (
        _PydanticLoggerBase,
    )
else:
    raise ImportError(
        f"eliot requires Python "
        f"{_ELIOT_MIN_PYTHON[0]}.{_ELIOT_MIN_PYTHON[1]}+, "
        f"but running on Python "
        f"{sys.version_info.major}.{sys.version_info.minor}"
    )


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    name: str


if TYPE_CHECKING:

    class _EliotLoggerAdapter(BaseModel, _Logger):
        model_config: ClassVar[ConfigDict]
        name: str

        def debug(self, msg: str, *args: object, **kwargs: object) -> None: ...

        def info(self, msg: str, *args: object, **kwargs: object) -> None: ...

        def warning(
            self, msg: str, *args: object, **kwargs: object
        ) -> None: ...

        def error(self, msg: str, *args: object, **kwargs: object) -> None: ...

        def critical(
            self, msg: str, *args: object, **kwargs: object
        ) -> None: ...

        def exception(
            self, msg: str, *args: object, **kwargs: object
        ) -> None: ...

else:

    class _EliotLoggerAdapter(BaseModel):
        model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

        name: str

        def _log(self, level: str, msg: str, **kwargs: object) -> None:
            log_message(
                message_type=self.name,
                log_level=level,
                message=msg,
                **kwargs,
            )

        def debug(self, msg: str, *args: object, **kwargs: object) -> None:
            self._log("debug", msg % args if args else msg, **kwargs)

        def info(self, msg: str, *args: object, **kwargs: object) -> None:
            self._log("info", msg % args if args else msg, **kwargs)

        def warning(self, msg: str, *args: object, **kwargs: object) -> None:
            self._log("warning", msg % args if args else msg, **kwargs)

        def error(self, msg: str, *args: object, **kwargs: object) -> None:
            self._log("error", msg % args if args else msg, **kwargs)

        def critical(self, msg: str, *args: object, **kwargs: object) -> None:
            self._log("critical", msg % args if args else msg, **kwargs)

        def exception(self, msg: str, *args: object, **kwargs: object) -> None:
            self._log("exception", msg % args if args else msg, **kwargs)


if not issubclass(_EliotLoggerAdapter, _LoggerProtocol):
    raise ValueError(
        f"{_EliotLoggerAdapter.__name__} is not an subclass of {_LoggerProtocol.__name__}"
    )


class _PydanticEliotLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        return _EliotLoggerAdapter(name=self.name)
