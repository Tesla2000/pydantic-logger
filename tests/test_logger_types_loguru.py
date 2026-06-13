import importlib
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import pydantic_logger


def test_loguru_logger_creates_and_logs() -> None:
    logger = pydantic_logger.PydanticLoguruLogger(name="test.loguru")
    logger.info("hello from loguru")


def test_loguru_issubclass_guard_raises() -> None:
    import pydantic_logger._logger_types._loguru as loguru_mod  # ignore

    fake_loguru_logger = MagicMock()
    fake_loguru_logger._logger = MagicMock()
    fake_loguru_logger._logger.Logger = object
    original_import = __import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "loguru._logger":
            return fake_loguru_logger._logger
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    sys.modules.pop("pydantic_logger._logger_types._loguru", None)
    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises((ValueError, AttributeError)):
            importlib.import_module("pydantic_logger._logger_types._loguru")
    sys.modules["pydantic_logger._logger_types._loguru"] = loguru_mod
