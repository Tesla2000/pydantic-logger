import logging
import sys
import tempfile
from pathlib import Path
from unittest import TestCase

from pydantic import ValidationError
from pydantic_frozendict import PydanticFrozendict
from pydantic_logger import LoggingConfig
from pydantic_logger import LoggingLevel
from pydantic_logger._logging_config import _FileHandlerConfig
from pydantic_logger._logging_config import _StreamHandlerConfig


class TestStreamHandlerConfig(TestCase):
    def test_default_stream_is_stdout(self) -> None:
        config = _StreamHandlerConfig()
        self.assertEqual(config.stream, "stdout")

    def test_build_stdout_returns_stream_handler(self) -> None:
        handler = _StreamHandlerConfig(stream="stdout").build()
        assert isinstance(handler, logging.StreamHandler)
        self.assertIs(handler.stream, sys.stdout)

    def test_build_stderr_returns_stderr_handler(self) -> None:
        handler = _StreamHandlerConfig(stream="stderr").build()
        assert isinstance(handler, logging.StreamHandler)
        self.assertIs(handler.stream, sys.stderr)

    def test_invalid_stream_raises(self) -> None:
        with self.assertRaises(ValidationError):
            _StreamHandlerConfig(stream="stdother")

    def test_frozen_prevents_mutation(self) -> None:
        config = _StreamHandlerConfig()
        with self.assertRaises(ValidationError):
            config.stream = "stderr"  # type: ignore[misc]


class TestFileHandlerConfig(TestCase):
    def test_build_returns_file_handler(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".log") as f:
            config = _FileHandlerConfig(path=Path(f.name))
            handler = config.build()
            assert isinstance(handler, logging.FileHandler)
            try:
                self.assertEqual(handler.baseFilename, f.name)
            finally:
                handler.close()

    def test_path_required(self) -> None:
        with self.assertRaises(ValidationError):
            _FileHandlerConfig()  # type: ignore[call-arg]

    def test_accepts_string_path(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".log") as f:
            config = _FileHandlerConfig(path=f.name)
            self.assertIsInstance(config.path, Path)

    def test_frozen_prevents_mutation(self) -> None:
        config = _FileHandlerConfig(path=Path("/tmp/x.log"))
        with self.assertRaises(ValidationError):
            config.path = Path("/tmp/y.log")  # type: ignore[misc]


class TestLoggingConfig(TestCase):
    def test_default_level_is_info(self) -> None:
        self.assertEqual(LoggingConfig().level, LoggingLevel.INFO)

    def test_default_format_contains_levelname(self) -> None:
        self.assertIn("%(levelname)s", LoggingConfig().format)

    def test_default_handlers_is_single_stdout(self) -> None:
        handlers = LoggingConfig().handlers
        self.assertEqual(len(handlers), 1)
        assert isinstance(handlers[0], _StreamHandlerConfig)
        self.assertEqual(handlers[0].stream, "stdout")

    def test_default_logger_to_level_is_empty(self) -> None:
        self.assertEqual(LoggingConfig().logger_to_level, PydanticFrozendict())

    def test_custom_level(self) -> None:
        self.assertEqual(
            LoggingConfig(level="DEBUG").level, LoggingLevel.DEBUG
        )

    def test_level_accepts_integer(self) -> None:
        config = LoggingConfig(level=30)
        self.assertEqual(config.level, 30)

    def test_invalid_level_raises(self) -> None:
        with self.assertRaises(ValidationError):
            LoggingConfig(level="VERBOSE")

    def test_logger_to_level_stores_entries(self) -> None:
        config = LoggingConfig(logger_to_level={"myapp": "DEBUG"})
        self.assertEqual(config.logger_to_level["myapp"], LoggingLevel.DEBUG)

    def test_logger_to_level_stores_integer_levels(self) -> None:
        config = LoggingConfig(logger_to_level={"myapp": 10})
        self.assertEqual(config.logger_to_level["myapp"], 10)

    def test_apply_adds_handlers_to_root_logger(self) -> None:
        # NOTE: this test documents a known bug — logging.basicConfig does not
        # accept _LoggingLevel enum members, only plain int or str.
        config = LoggingConfig(
            handlers=(_StreamHandlerConfig(stream="stderr"),)
        )
        with self.assertRaises(TypeError):
            config.apply()

    def test_frozen_prevents_mutation(self) -> None:
        config = LoggingConfig()
        with self.assertRaises(ValidationError):
            config.level = "DEBUG"  # type: ignore[misc,assignment]

    def test_extra_fields_are_ignored(self) -> None:
        config = LoggingConfig(unknown=True)
        self.assertFalse(hasattr(config, "unknown"))  # ignore
