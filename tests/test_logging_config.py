import logging
import sys
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_frozendict import PydanticFrozendict

from pydantic_logger import LoggingConfig
from pydantic_logger import LoggingLevel
from pydantic_logger._logging_config import _FileHandlerConfig
from pydantic_logger._logging_config import _StreamHandlerConfig


def test_default_stream_is_stdout() -> None:
    config = _StreamHandlerConfig()
    assert config.stream == "stdout"


def test_build_stdout_returns_stream_handler() -> None:
    handler = _StreamHandlerConfig(stream="stdout").build()
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout


def test_build_stderr_returns_stderr_handler() -> None:
    handler = _StreamHandlerConfig(stream="stderr").build()
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stderr


def test_invalid_stream_raises() -> None:
    with pytest.raises(ValidationError):
        _StreamHandlerConfig(stream="stdother")


def test_stream_frozen_prevents_mutation() -> None:
    config = _StreamHandlerConfig()
    with pytest.raises(ValidationError):
        config.stream = "stderr"  # type: ignore[misc]


def test_file_handler_build_returns_file_handler() -> None:
    with tempfile.NamedTemporaryFile(suffix=".log") as f:
        config = _FileHandlerConfig(path=Path(f.name))
        handler = config.build()
        assert isinstance(handler, logging.FileHandler)
        try:
            assert handler.baseFilename == f.name
        finally:
            handler.close()


def test_file_handler_path_required() -> None:
    with pytest.raises(ValidationError):
        _FileHandlerConfig()  # type: ignore[call-arg]


def test_file_handler_accepts_string_path() -> None:
    with tempfile.NamedTemporaryFile(suffix=".log") as f:
        config = _FileHandlerConfig(path=f.name)
        assert isinstance(config.path, Path)


def test_file_handler_frozen_prevents_mutation() -> None:
    config = _FileHandlerConfig(path=Path("/tmp/x.log"))
    with pytest.raises(ValidationError):
        config.path = Path("/tmp/y.log")  # type: ignore[misc]


def test_logging_config_default_level_is_info() -> None:
    assert LoggingConfig().level == LoggingLevel.INFO


def test_logging_config_default_format_contains_levelname() -> None:
    assert "%(levelname)s" in LoggingConfig().format


def test_logging_config_default_handlers_is_single_stdout() -> None:
    handlers = LoggingConfig().handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], _StreamHandlerConfig)
    assert handlers[0].stream == "stdout"


def test_logging_config_default_logger_to_level_is_empty() -> None:
    assert LoggingConfig().logger_to_level == PydanticFrozendict()


def test_logging_config_custom_level() -> None:
    assert LoggingConfig(level="DEBUG").level == LoggingLevel.DEBUG


def test_logging_config_level_accepts_integer() -> None:
    config = LoggingConfig(level=30)
    assert config.level == 30


def test_logging_config_invalid_level_raises() -> None:
    with pytest.raises(ValidationError):
        LoggingConfig(level="VERBOSE")


def test_logging_config_logger_to_level_stores_entries() -> None:
    config = LoggingConfig(logger_to_level={"myapp": "DEBUG"})
    assert config.logger_to_level["myapp"] == LoggingLevel.DEBUG


def test_logging_config_logger_to_level_stores_integer_levels() -> None:
    config = LoggingConfig(logger_to_level={"myapp": 10})
    assert config.logger_to_level["myapp"] == 10


def test_logging_config_apply_adds_handlers_to_root_logger() -> None:
    config = LoggingConfig(handlers=(_StreamHandlerConfig(stream="stderr"),))
    config.apply()


def test_logging_config_apply_sets_per_logger_level() -> None:
    config = LoggingConfig(logger_to_level={"apply.test.logger": "DEBUG"})
    config.apply()
    assert logging.getLogger("apply.test.logger").level == logging.DEBUG


def test_logging_config_frozen_prevents_mutation() -> None:
    config = LoggingConfig()
    with pytest.raises(ValidationError):
        config.level = "DEBUG"  # type: ignore[misc,assignment]


def test_logging_config_extra_fields_are_ignored() -> None:
    config = LoggingConfig(unknown=True)
    assert not hasattr(config, "unknown")  # ignore
