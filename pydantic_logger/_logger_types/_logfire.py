from collections.abc import Sequence
from types import TracebackType
from typing import Any
from typing import ClassVar
from typing import Protocol
from typing import runtime_checkable
from typing import TYPE_CHECKING
from typing import Union

import logfire
from logfire import Logfire
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from pydantic_logger._logger_protocol import _LoggerProtocol
from pydantic_logger._pydantic_logger_base import _PydanticLoggerBase

_ExcInfo = Union[
    tuple[type[BaseException], BaseException, "TracebackType | None"],
    tuple[None, None, None],
    BaseException,
    bool,
    None,
]


def _create_scoped_logfire(data: dict[str, object]) -> Logfire:
    name = data.get("name")
    if not isinstance(name, str):
        raise ValueError(f"name must be a str, got {name!r}")
    return logfire.with_settings(custom_scope_suffix=name)


@runtime_checkable
class _Logger(_LoggerProtocol, Protocol):
    name: str


if TYPE_CHECKING:

    class _LogfireLoggerAdapter(BaseModel, _Logger):
        model_config: ClassVar[ConfigDict]
        name: str
        scoped: Logfire = Field(default=None)  # type: ignore[assignment]

        def debug(
            self, msg: str, *args: object, **attributes: Any
        ) -> None: ...

        def info(self, msg: str, *args: object, **attributes: Any) -> None: ...

        def warning(
            self, msg: str, *args: object, **attributes: Any
        ) -> None: ...

        def error(
            self, msg: str, *args: object, **attributes: Any
        ) -> None: ...

        def critical(
            self, msg: str, *args: object, **attributes: Any
        ) -> None: ...

        def exception(
            self, msg: str, *args: object, **attributes: Any
        ) -> None: ...

else:

    class _LogfireLoggerAdapter(BaseModel):
        model_config: ClassVar[ConfigDict] = ConfigDict(
            frozen=True, arbitrary_types_allowed=True
        )

        name: str
        scoped: Logfire = Field(
            default_factory=_create_scoped_logfire, exclude=True
        )

        def debug(
            self,
            msg: str,
            *args: object,
            _tags: "Sequence[str] | None" = None,
            _exc_info: _ExcInfo = False,
            **attributes: Any,
        ) -> None:
            self.scoped.debug(
                msg % args if args else msg,
                _tags=_tags,
                _exc_info=_exc_info,
                **attributes,
            )

        def info(
            self,
            msg: str,
            *args: object,
            _tags: "Sequence[str] | None" = None,
            _exc_info: _ExcInfo = False,
            **attributes: Any,
        ) -> None:
            self.scoped.info(
                msg % args if args else msg,
                _tags=_tags,
                _exc_info=_exc_info,
                **attributes,
            )

        def warning(
            self,
            msg: str,
            *args: object,
            _tags: "Sequence[str] | None" = None,
            _exc_info: _ExcInfo = False,
            **attributes: Any,
        ) -> None:
            self.scoped.warn(
                msg % args if args else msg,
                _tags=_tags,
                _exc_info=_exc_info,
                **attributes,
            )

        def error(
            self,
            msg: str,
            *args: object,
            _tags: "Sequence[str] | None" = None,
            _exc_info: _ExcInfo = False,
            **attributes: Any,
        ) -> None:
            self.scoped.error(
                msg % args if args else msg,
                _tags=_tags,
                _exc_info=_exc_info,
                **attributes,
            )

        def critical(
            self,
            msg: str,
            *args: object,
            _tags: "Sequence[str] | None" = None,
            _exc_info: _ExcInfo = False,
            **attributes: Any,
        ) -> None:
            self.scoped.fatal(
                msg % args if args else msg,
                _tags=_tags,
                _exc_info=_exc_info,
                **attributes,
            )

        def exception(
            self,
            msg: str,
            *args: object,
            _tags: "Sequence[str] | None" = None,
            _exc_info: _ExcInfo = True,
            **attributes: Any,
        ) -> None:
            self.scoped.exception(
                msg % args if args else msg,
                _tags=_tags,
                _exc_info=_exc_info,
                **attributes,
            )

    if not issubclass(_LogfireLoggerAdapter, _LoggerProtocol):
        raise ValueError(
            f"{_LogfireLoggerAdapter.__name__} is not a subclass of {_LoggerProtocol.__name__}"
        )


class _PydanticLogfireLogger(_PydanticLoggerBase[_Logger]):
    def _create_logger(self) -> _Logger:
        return _LogfireLoggerAdapter(name=self.name)
