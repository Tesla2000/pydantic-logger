import importlib
import sys
import types
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import structlog

import pydantic_logger


def test_structlog_logger_creates_and_logs() -> None:
    import pydantic_logger._logger_types._structlog as structlog_mod  # ignore

    mock_bound_logger = MagicMock(spec=structlog.stdlib.BoundLogger)
    with patch.object(structlog_mod, "structlog") as mock_structlog:
        mock_structlog.get_logger.return_value = mock_bound_logger
        mock_structlog.stdlib.BoundLogger = structlog.stdlib.BoundLogger
        logger = pydantic_logger.PydanticStructlogLogger(name="test.structlog")
    logger.info("hello from structlog")


def test_structlog_issubclass_guard_raises() -> None:
    import pydantic_logger._logger_types._structlog as structlog_mod  # ignore

    original_import = __import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "structlog":
            fake = types.ModuleType("structlog")
            fake_stdlib = types.ModuleType("structlog.stdlib")  # type: ignore[attr-defined]

            class _FakeBoundLogger:
                pass

            fake_stdlib.BoundLogger = _FakeBoundLogger  # type: ignore[attr-defined]
            fake.stdlib = fake_stdlib  # type: ignore[attr-defined]
            fake.get_logger = lambda name: _FakeBoundLogger()  # type: ignore[attr-defined]
            return fake
        if name == "structlog.stdlib":
            fake_stdlib = types.ModuleType("structlog.stdlib")

            class _FakeBoundLogger:
                pass

            fake_stdlib.BoundLogger = _FakeBoundLogger  # type: ignore[attr-defined]
            return fake_stdlib
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    sys.modules.pop("pydantic_logger._logger_types._structlog", None)
    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ValueError, match="is not an subclass"):
            importlib.import_module("pydantic_logger._logger_types._structlog")
    sys.modules["pydantic_logger._logger_types._structlog"] = structlog_mod
