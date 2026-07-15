import importlib
import sys
from typing import Protocol
from typing import runtime_checkable
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import pydantic_logger
import pydantic_logger._logger_protocol as protocol_mod
import pydantic_logger._logger_types._logfire as logfire_mod
from pydantic_logger._logger_types._logfire import _create_scoped_logfire
from pydantic_logger._logger_types._logfire import _LogfireLoggerAdapter


def test_logfire_logger_creates_and_logs() -> None:
    logger = pydantic_logger.PydanticLogfireLogger(name="test.logfire")
    logger.info("hello from logfire")


def test_logfire_logger_all_methods() -> None:
    mock_scoped = MagicMock()
    adapter = _LogfireLoggerAdapter.model_construct(
        **{"name": "test.logfire.all", "scoped": mock_scoped}
    )
    adapter.debug("dbg %s", "x")
    mock_scoped.debug.assert_called_once_with(
        "dbg x", _tags=None, _exc_info=False
    )
    adapter.info("inf")
    mock_scoped.info.assert_called_once_with(
        "inf", _tags=None, _exc_info=False
    )
    adapter.warning("warn")
    mock_scoped.warn.assert_called_once_with(
        "warn", _tags=None, _exc_info=False
    )
    adapter.error("err")
    mock_scoped.error.assert_called_once_with(
        "err", _tags=None, _exc_info=False
    )
    adapter.critical("crit")
    mock_scoped.fatal.assert_called_once_with(
        "crit", _tags=None, _exc_info=False
    )
    adapter.exception("exc")
    mock_scoped.exception.assert_called_once_with(
        "exc", _tags=None, _exc_info=True
    )


def test_logfire_adapter_is_subclass_of_logger_protocol() -> None:
    assert issubclass(_LogfireLoggerAdapter, protocol_mod._LoggerProtocol)


def test_logfire_issubclass_guard_raises() -> None:
    @runtime_checkable
    class _StrictProtocol(Protocol):
        def nonexistent_method(self) -> None: ...

    sys.modules.pop("pydantic_logger._logger_types._logfire", None)
    with patch.object(
        protocol_mod, protocol_mod._LoggerProtocol.__name__, _StrictProtocol
    ):
        with pytest.raises(ValueError, match="is not a subclass"):
            importlib.import_module("pydantic_logger._logger_types._logfire")
    sys.modules["pydantic_logger._logger_types._logfire"] = logfire_mod


def test_logfire_factory_raises_when_name_not_str() -> None:
    with pytest.raises(ValueError, match="name must be a str"):
        _create_scoped_logfire({"name": 123})


def test_logger_types_getattr_logfire() -> None:
    assert (
        pydantic_logger._logger_types.PydanticLogfireLogger
        is pydantic_logger.PydanticLogfireLogger
    )
