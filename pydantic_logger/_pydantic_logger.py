import inspect
import logging
import os
from logging import Logger
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import InstanceOf
from pydantic import PositiveInt

from pydantic_logger._logging_level import (
    _LoggingLevelAnnotation as LoggingLevelAnnotation,
)


def _get_caller_module_name() -> str:
    frame = inspect.currentframe()
    try:
        while frame is not None:
            module_name = frame.f_globals.get("__name__")
            if module_name and not isinstance(module_name, str):
                module_name = None
            if (
                module_name
                and not module_name.startswith("pydantic_logger")
                and not module_name.startswith("pydantic")
            ):
                return module_name
            frame = frame.f_back
        raise ValueError(
            "Could not determine caller module name from call stack"
        )
    finally:
        del frame


def _create_logger(validated_data: dict[str, object]) -> Logger:
    if "name" not in validated_data or "level" not in validated_data:
        raise ValueError(
            f"Logger name or level not in validated data {validated_data}"
        )
    name = validated_data["name"]
    assert isinstance(name, str)
    logger = logging.getLogger(name)
    level = validated_data["level"]
    if level is not None:
        assert isinstance(level, (str, int))
        logger.setLevel(level)
    return logger


class _PydanticLogger(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
    )

    level: Optional[LoggingLevelAnnotation] = None
    name: str = Field(default_factory=_get_caller_module_name)
    stacklevel: Union[PositiveInt, None] = Field(
        default_factory=lambda: os.getenv("PYDANTIC_LOGGER_STACK_LEVEL"),
        validate_default=True,
    )
    logger: InstanceOf[Logger] = Field(
        default_factory=_create_logger, exclude=True
    )

    def _set_stacklevel_if_configured(self, kwargs: dict[str, Any]) -> None:
        if self.stacklevel is None:
            return
        kwargs.setdefault("stacklevel", self.stacklevel)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.exception(msg, *args, **kwargs)

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        self._set_stacklevel_if_configured(kwargs)
        self.logger.log(level, msg, *args, **kwargs)
