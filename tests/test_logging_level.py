import logging
from unittest import TestCase

from pydantic import BaseModel
from pydantic import ValidationError
from pydantic_logger import LoggingLevel
from pydantic_logger import LoggingLevelAnnotation


class TestLoggingLevel(TestCase):
    def test_all_enum_values_are_strings(self) -> None:
        for member in LoggingLevel:
            self.assertIsInstance(member.value, str)

    def test_enum_members(self) -> None:
        self.assertEqual(LoggingLevel.DEBUG, "DEBUG")
        self.assertEqual(LoggingLevel.INFO, "INFO")
        self.assertEqual(LoggingLevel.WARNING, "WARNING")
        self.assertEqual(LoggingLevel.ERROR, "ERROR")
        self.assertEqual(LoggingLevel.CRITICAL, "CRITICAL")

    def test_enum_value_is_string(self) -> None:
        self.assertEqual(LoggingLevel.INFO.value, "INFO")


class _Model(BaseModel):
    level: LoggingLevelAnnotation


class TestLoggingLevelAnnotation(TestCase):
    def test_accepts_uppercase_string(self) -> None:
        self.assertEqual(_Model(level="INFO").level, LoggingLevel.INFO)

    def test_accepts_lowercase_string(self) -> None:
        self.assertEqual(_Model(level="debug").level, LoggingLevel.DEBUG)

    def test_accepts_mixed_case_string(self) -> None:
        self.assertEqual(_Model(level="Warning").level, LoggingLevel.WARNING)

    def test_accepts_integer(self) -> None:
        # Integers pass through without conversion
        result = _Model(level=10).level
        self.assertEqual(result, 10)

    def test_rejects_invalid_string(self) -> None:
        with self.assertRaises(ValidationError):
            _Model(level="VERBOSE")

    def test_all_enum_names_accepted(self) -> None:
        for member in LoggingLevel:
            model = _Model(level=member.value)
            self.assertEqual(model.level, member)


class TestLoggingLevelCompatibility(TestCase):
    """Verify that validated level values can be passed to logging.setLevel."""

    def setUp(self) -> None:
        self.logger = logging.getLogger("compat.test")

    def test_plain_int_works_with_set_level(self) -> None:
        self.logger.setLevel(10)
        self.assertEqual(self.logger.level, 10)

    def test_plain_str_works_with_set_level(self) -> None:
        self.logger.setLevel("WARNING")
        self.assertEqual(self.logger.level, logging.WARNING)

    def test_enum_member_works_with_set_level(self) -> None:
        # _LoggingLevel is a str-enum; verify logging.setLevel accepts it.
        self.logger.setLevel(LoggingLevel.WARNING)
        self.assertEqual(self.logger.level, logging.WARNING)

    def test_enum_int_value_works_with_set_level(self) -> None:
        validated_int = _Model(level=20).level
        self.logger.setLevel(validated_int)
        self.assertEqual(self.logger.level, logging.INFO)
