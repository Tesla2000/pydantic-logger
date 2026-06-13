import sys

_PICOLOGGING_MIN_PYTHON = (3, 7)
_PICOLOGGING_MAX_PYTHON = (3, 12)

if _PICOLOGGING_MIN_PYTHON <= sys.version_info[:2] <= _PICOLOGGING_MAX_PYTHON:
    from typing import Protocol, runtime_checkable, Optional

    import picologging

    from pydantic_logger._logger_protocol import _LoggerProtocol
    from pydantic_logger._pydantic_logger_base import (
        _PydanticLoggerBase,
    )
else:
    raise ImportError(
        f"picologging supports Python "
        f"{_PICOLOGGING_MIN_PYTHON[0]}.{_PICOLOGGING_MIN_PYTHON[1]}"
        f"-{_PICOLOGGING_MAX_PYTHON[0]}.{_PICOLOGGING_MAX_PYTHON[1]}, "
        f"but running on Python "
        f"{sys.version_info.major}.{sys.version_info.minor}"
    )


if not issubclass(picologging.Logger, _LoggerProtocol):
    raise ValueError(
        f"{picologging.Logger.__name__} is not an subclass of {_LoggerProtocol.__name__}"
    )


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    def setLevel(self, level: object) -> None: ...


class _PydanticPicologgingLogger(_PydanticLoggerBase[_Logger]):
    level: Optional[int] = None

    def _create_logger(self) -> _Logger:
        logger = picologging.getLogger(self.name)
        if self.level is not None:
            logger.setLevel(self.level)
        assert isinstance(logger, _Logger)
        return logger
