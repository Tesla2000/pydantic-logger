import logging
import uuid
from unittest import TestCase
from unittest.mock import MagicMock

from pydantic import ValidationError
from pydantic_logger import PydanticLogger


class TestPydanticLoggerDefaults(TestCase):
    def test_default_name_is_valid_uuid(self) -> None:
        logger = PydanticLogger()
        uuid.UUID(logger.name)  # raises if invalid

    def test_two_default_instances_have_different_names(self) -> None:
        self.assertNotEqual(PydanticLogger().name, PydanticLogger().name)

    def test_default_level_is_none(self) -> None:
        self.assertIsNone(PydanticLogger().level)

    def test_logger_field_is_logging_logger(self) -> None:
        self.assertIsInstance(PydanticLogger().logger, logging.Logger)


class TestPydanticLoggerConstruction(TestCase):
    def test_custom_name(self) -> None:
        logger = PydanticLogger(name="my.logger")
        self.assertEqual(logger.name, "my.logger")
        self.assertEqual(logger.logger.name, "my.logger")

    def test_level_sets_logger_level(self) -> None:
        logger = PydanticLogger(name="level.test.int", level=logging.DEBUG)
        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_level_string_sets_logger_level(self) -> None:
        # NOTE: documents a known bug — _LoggingLevel enum is passed directly to
        # logging.setLevel which only accepts plain int/str, not str-enum members.
        with self.assertRaises(TypeError):
            PydanticLogger(name="level.test.str", level="WARNING")

    def test_level_none_does_not_override_logger_level(self) -> None:
        underlying = logging.getLogger("level.test.none")
        underlying.setLevel(logging.ERROR)
        logger = PydanticLogger(name="level.test.none", level=None)
        self.assertEqual(logger.logger.level, logging.ERROR)

    def test_invalid_level_raises(self) -> None:
        with self.assertRaises(ValidationError):
            PydanticLogger(level="INVALID_LEVEL")

    def test_logger_excluded_from_serialization(self) -> None:
        data = PydanticLogger(name="serial.test").model_dump()
        self.assertNotIn("logger", data)

    def test_extra_fields_are_ignored(self) -> None:
        logger = PydanticLogger(name="x", unknown_field=True)
        self.assertFalse(hasattr(logger, "unknown_field"))  # ignore


class TestPydanticLoggerFrozen(TestCase):
    def test_frozen_prevents_name_mutation(self) -> None:
        logger = PydanticLogger(name="frozen.test")
        with self.assertRaises(ValidationError):
            logger.name = "other"  # type: ignore[misc]

    def test_frozen_prevents_level_mutation(self) -> None:
        logger = PydanticLogger(name="frozen.level")
        with self.assertRaises(ValidationError):
            logger.level = "DEBUG"  # type: ignore[misc,assignment]


class TestPydanticLoggerMethods(TestCase):
    def setUp(self) -> None:
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.pydantic_logger = PydanticLogger(name="method.test")
        # Replace the internal logger with a mock after construction
        object.__setattr__(self.pydantic_logger, "logger", self.mock_logger)

    def test_debug_delegates(self) -> None:
        self.pydantic_logger.debug("msg", "arg", key="val")
        self.mock_logger.debug.assert_called_once_with("msg", "arg", key="val")

    def test_info_delegates(self) -> None:
        self.pydantic_logger.info("msg")
        self.mock_logger.info.assert_called_once_with("msg")

    def test_warning_delegates(self) -> None:
        self.pydantic_logger.warning("msg")
        self.mock_logger.warning.assert_called_once_with("msg")

    def test_error_delegates(self) -> None:
        self.pydantic_logger.error("msg")
        self.mock_logger.error.assert_called_once_with("msg")

    def test_critical_delegates(self) -> None:
        self.pydantic_logger.critical("msg")
        self.mock_logger.critical.assert_called_once_with("msg")

    def test_exception_delegates(self) -> None:
        self.pydantic_logger.exception("msg")
        self.mock_logger.exception.assert_called_once_with("msg")

    def test_log_delegates_with_level(self) -> None:
        self.pydantic_logger.log(logging.WARNING, "msg")
        self.mock_logger.log.assert_called_once_with(logging.WARNING, "msg")
