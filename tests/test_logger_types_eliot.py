import importlib
import sys
from typing import Protocol
from typing import runtime_checkable
from unittest.mock import patch

import pytest

import pydantic_logger
import pydantic_logger._logger_protocol as protocol_mod

eliot_mod = pytest.importorskip(
    "pydantic_logger._logger_types._eliot", exc_type=ImportError
)


def test_eliot_logger_creates_and_logs() -> None:
    logger = pydantic_logger.PydanticEliotLogger(name="test.eliot")
    logger.info("hello from eliot")


def test_eliot_adapter_all_log_methods() -> None:
    logger = pydantic_logger.PydanticEliotLogger(name="test.eliot.methods")
    logger.debug("dbg")
    logger.warning("warn")
    logger.error("err")
    logger.critical("crit")
    logger.exception("exc")


def test_eliot_issubclass_guard_raises() -> None:
    @runtime_checkable
    class _StrictProtocol(Protocol):
        def nonexistent_method(self) -> None: ...

    sys.modules.pop("pydantic_logger._logger_types._eliot", None)
    with patch.object(
        protocol_mod, protocol_mod._LoggerProtocol.__name__, _StrictProtocol
    ):
        with pytest.raises(ValueError, match="is not an subclass"):
            importlib.import_module("pydantic_logger._logger_types._eliot")
    sys.modules["pydantic_logger._logger_types._eliot"] = eliot_mod


def test_eliot_import_error_on_old_python() -> None:
    import pydantic_logger._logger_types._eliot as eliot_mod  # ignore

    sys.modules.pop("pydantic_logger._logger_types._eliot", None)
    with patch("sys.version_info", (3, 9)):
        with pytest.raises((ImportError, Exception)):
            importlib.import_module("pydantic_logger._logger_types._eliot")
    sys.modules["pydantic_logger._logger_types._eliot"] = eliot_mod
