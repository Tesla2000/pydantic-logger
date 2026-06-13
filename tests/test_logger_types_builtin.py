import importlib
import logging
import sys
import types
from unittest.mock import patch

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


def test_builtin_issubclass_guard_raises() -> None:
    import pydantic_logger._logger_types._builtin as builtin_mod  # ignore

    fake_logging = _make_fake_module("logging", "Logger", object)
    original_import = __import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "logging":
            return fake_logging
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    sys.modules.pop("pydantic_logger._logger_types._builtin", None)
    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ValueError, match="is not an subclass"):
            importlib.import_module("pydantic_logger._logger_types._builtin")
    sys.modules["pydantic_logger._logger_types._builtin"] = builtin_mod


def test_builtin_create_logger_isinstance_guard_raises() -> None:
    def fake_getLogger(name: str) -> object:
        class _Fake:
            pass

        return _Fake()

    with patch.object(
        logging, logging.getLogger.__name__, side_effect=fake_getLogger
    ):
        with pytest.raises(ValueError):
            pydantic_logger.PydanticBuiltinLogger(name="test.builtin.guard")
