import importlib
import sys
import types
from unittest.mock import patch

import logbook
import pytest

import pydantic_logger


def _make_fake_module(
    real_name: str, fake_attr: str, fake_value: object
) -> object:
    real_module = importlib.import_module(real_name)
    fake = types.ModuleType(real_name)
    fake.__dict__.update(real_module.__dict__)
    fake.__dict__[fake_attr] = fake_value
    return fake


def test_logbook_logger_creates_and_logs() -> None:
    logger = pydantic_logger.PydanticLogbookLogger(name="test.logbook")
    logger.info("hello from logbook")


def test_logbook_logger_with_int_level() -> None:
    logger = pydantic_logger.PydanticLogbookLogger(
        name="test.logbook.level", level=logbook.DEBUG
    )
    logger.debug("hello at debug")


def test_logbook_logger_with_str_level() -> None:
    logger = pydantic_logger.PydanticLogbookLogger(
        name="test.logbook.strlevel", level="WARNING"
    )
    logger.warning("hello at warning")


def test_logbook_issubclass_guard_raises() -> None:
    import pydantic_logger._logger_types._logbook as logbook_mod  # ignore

    fake_logbook = _make_fake_module("logbook", "Logger", object)
    original_import = __import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "logbook":
            return fake_logbook
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    sys.modules.pop("pydantic_logger._logger_types._logbook", None)
    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ValueError, match="is not an subclass"):
            importlib.import_module("pydantic_logger._logger_types._logbook")
    sys.modules["pydantic_logger._logger_types._logbook"] = logbook_mod
