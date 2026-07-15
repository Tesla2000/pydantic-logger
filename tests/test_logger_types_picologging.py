import importlib
import sys
import types
from unittest.mock import patch

import pytest

import pydantic_logger

picologging = pytest.importorskip("picologging")


def _make_fake_module(
    real_name: str, fake_attr: str, fake_value: object
) -> object:
    real_module = importlib.import_module(real_name)
    fake = types.ModuleType(real_name)
    fake.__dict__.update(real_module.__dict__)
    fake.__dict__[fake_attr] = fake_value
    return fake


def test_picologging_logger_creates_and_logs() -> None:
    logger = pydantic_logger.PydanticPicologgingLogger(name="test.picologging")
    logger.info("hello from picologging")


def test_picologging_logger_with_level() -> None:
    logger = pydantic_logger.PydanticPicologgingLogger(
        name="test.picologging.level", level=picologging.DEBUG
    )
    logger.debug("hello at debug")


def test_picologging_logger_level_is_set() -> None:
    logger = pydantic_logger.PydanticPicologgingLogger(
        name="test.picologging.setlevel", level=picologging.WARNING
    )
    assert logger.logger.level == picologging.WARNING


def test_picologging_issubclass_guard_raises() -> None:
    import pydantic_logger._logger_types._picologging as pico_mod  # ignore

    fake_picologging = _make_fake_module("picologging", "Logger", object)
    original_import = __import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "picologging":
            return fake_picologging
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    sys.modules.pop("pydantic_logger._logger_types._picologging", None)
    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ValueError, match="is not an subclass"):
            importlib.import_module(
                "pydantic_logger._logger_types._picologging"
            )
    sys.modules["pydantic_logger._logger_types._picologging"] = pico_mod


def test_picologging_import_error_on_unsupported_python() -> None:
    import pydantic_logger._logger_types._picologging as pico_mod  # ignore

    original_import = __import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "picologging":
            raise ImportError("mocked unavailable")
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    sys.modules.pop("pydantic_logger._logger_types._picologging", None)
    with patch("builtins.__import__", side_effect=mock_import):
        with patch("sys.version_info", (3, 13)):
            with pytest.raises((ImportError, Exception)):
                importlib.import_module(
                    "pydantic_logger._logger_types._picologging"
                )
    sys.modules["pydantic_logger._logger_types._picologging"] = pico_mod
