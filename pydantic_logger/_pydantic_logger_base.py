import inspect
import typing
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Annotated
from typing import cast
from typing import ClassVar
from typing import Generic
from typing import get_args
from typing import Optional
from typing import Self
from typing import TYPE_CHECKING
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator
from pydantic import ModelWrapValidatorHandler

from pydantic_logger._logger_protocol import _LoggerProtocol
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


def _get_unique_bases(class_: type, bases: set[type]) -> Iterable[type]:
    for base in class_.__bases__:
        if base in bases:
            continue
        bases.add(base)
        yield base
        yield from _get_unique_bases(base, bases)


LoggerType = TypeVar("LoggerType", bound=_LoggerProtocol)


class _PydanticLoggerBase(BaseModel, Generic[LoggerType], ABC):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
    )

    level: Optional[LoggingLevelAnnotation] = None
    name: str = Field(default_factory=_get_caller_module_name)

    _logger: LoggerType
    if TYPE_CHECKING:
        logger: Annotated[LoggerType, Field(exclude=True)] = cast(
            LoggerType, object
        )

        @classmethod
        def _logger_type_validator(cls, logger: object) -> LoggerType: ...

        @model_validator(mode="wrap")
        @classmethod
        def _add_logger(
            cls, data: object, handler: ModelWrapValidatorHandler[Self]
        ) -> Self: ...

    else:

        @property
        def logger(self) -> LoggerType:
            return self._logger

        @classmethod
        def _logger_type_validator(cls, logger: object) -> LoggerType:
            logger_types = set()
            for class_ in _get_unique_bases(cls, set()):
                if class_ is _PydanticLoggerBase or not issubclass(
                    class_, BaseModel
                ):
                    continue
                origin_bases = getattr(class_, "__orig_bases__", ())  # ignore
                for base in origin_bases:
                    if not isinstance(base, typing._GenericAlias):
                        continue
                    for arg, generic_class in zip(
                        get_args(base),
                        class_.__pydantic_generic_metadata__["args"],
                        strict=True,
                    ):
                        if arg is LoggerType:
                            logger_types.add(generic_class)
            if len(logger_types) > 1:
                raise ValueError(
                    f"There was more than one {LoggerType.__name__} defined by {cls} {logger_types=}"
                )
            logger_type = tuple(logger_types)[0]
            if isinstance(logger, logger_type) and isinstance(
                logger, _LoggerProtocol
            ):
                return logger
            raise ValueError(
                f"{logger=} is not an instance of {logger_type} and {_LoggerProtocol.__name__}"
            )

        @model_validator(mode="wrap")
        @classmethod
        def _add_logger(
            cls, data: object, handler: ModelWrapValidatorHandler[Self]
        ) -> Self:
            validated_logger = handler(data)
            if isinstance(data, Mapping) and "logger" in data:
                validated_logger._logger = cls._logger_type_validator(
                    data["logger"]
                )
            else:
                validated_logger._logger = validated_logger._create_logger()
            return validated_logger

    @abstractmethod
    def _create_logger(self) -> LoggerType: ...

    def debug(self, msg: str, *args: object, **kwargs: object) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: object, **kwargs: object) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: object, **kwargs: object) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: object, **kwargs: object) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: object, **kwargs: object) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: object, **kwargs: object) -> None:
        self._set_stack_level_if_configured(kwargs)
        self.logger.exception(msg, *args, **kwargs)

    def _set_stack_level_if_configured(
        self, kwargs: dict[str, object]
    ) -> None:
        pass
