from typing import TYPE_CHECKING

from pydantic_logger._logger_types._builtin import (
    _PydanticBuiltinLogger as PydanticBuiltinLogger,
)

if TYPE_CHECKING:
    from pydantic_logger._logger_types._eliot import (
        _PydanticEliotLogger as PydanticEliotLogger,
    )
    from pydantic_logger._logger_types._logbook import (
        _PydanticLogbookLogger as PydanticLogbookLogger,
    )
    from pydantic_logger._logger_types._loguru import (
        _PydanticLoguruLogger as PydanticLoguruLogger,
    )
    from pydantic_logger._logger_types._picologging import (
        _PydanticPicologgingLogger as PydanticPicologgingLogger,
    )
    from pydantic_logger._logger_types._structlog import (
        _PydanticStructlogLogger as PydanticStructlogLogger,
    )

__all__ = [
    "PydanticBuiltinLogger",
    "PydanticLoguruLogger",
    "PydanticStructlogLogger",
    "PydanticLogbookLogger",
    "PydanticPicologgingLogger",
    "PydanticEliotLogger",
]


def __getattr__(name: str) -> object:
    if name == "PydanticLoguruLogger":
        from pydantic_logger._logger_types._loguru import (
            _PydanticLoguruLogger,
        )

        return _PydanticLoguruLogger
    if name == "PydanticStructlogLogger":
        from pydantic_logger._logger_types._structlog import (
            _PydanticStructlogLogger,
        )

        return _PydanticStructlogLogger
    if name == "PydanticLogbookLogger":
        from pydantic_logger._logger_types._logbook import (
            _PydanticLogbookLogger,
        )

        return _PydanticLogbookLogger
    if name == "PydanticPicologgingLogger":
        from pydantic_logger._logger_types._picologging import (
            _PydanticPicologgingLogger,
        )

        return _PydanticPicologgingLogger
    if name == "PydanticEliotLogger":
        from pydantic_logger._logger_types._eliot import (
            _PydanticEliotLogger,
        )

        return _PydanticEliotLogger
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
