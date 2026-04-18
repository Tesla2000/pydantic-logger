import logging

import pytest
from pydantic import BaseModel
from pydantic import ValidationError
from pydantic_logger import LoggingLevel
from pydantic_logger import LoggingLevelAnnotation


def test_all_enum_values_are_strings() -> None:
    for member in LoggingLevel:
        assert isinstance(member.value, str)


def test_enum_members() -> None:
    assert LoggingLevel.DEBUG == "DEBUG"
    assert LoggingLevel.INFO == "INFO"
    assert LoggingLevel.WARNING == "WARNING"
    assert LoggingLevel.ERROR == "ERROR"
    assert LoggingLevel.CRITICAL == "CRITICAL"


def test_enum_value_is_string() -> None:
    assert LoggingLevel.INFO.value == "INFO"


class _Model(BaseModel):
    level: LoggingLevelAnnotation


def test_annotation_accepts_uppercase_string() -> None:
    assert _Model(level="INFO").level == LoggingLevel.INFO


def test_annotation_accepts_lowercase_string() -> None:
    assert _Model(level="debug").level == LoggingLevel.DEBUG


def test_annotation_accepts_mixed_case_string() -> None:
    assert _Model(level="Warning").level == LoggingLevel.WARNING


def test_annotation_accepts_integer() -> None:
    result = _Model(level=10).level
    assert result == 10


def test_annotation_rejects_invalid_string() -> None:
    with pytest.raises(ValidationError):
        _Model(level="VERBOSE")


def test_annotation_all_enum_names_accepted() -> None:
    for member in LoggingLevel:
        model = _Model(level=member.value)
        assert model.level == member


def test_compat_plain_int_works_with_set_level() -> None:
    logger = logging.getLogger("compat.test")
    logger.setLevel(10)
    assert logger.level == 10


def test_compat_plain_str_works_with_set_level() -> None:
    logger = logging.getLogger("compat.test")
    logger.setLevel("WARNING")
    assert logger.level == logging.WARNING


def test_compat_enum_member_works_with_set_level() -> None:
    logger = logging.getLogger("compat.test")
    logger.setLevel(LoggingLevel.WARNING)
    assert logger.level == logging.WARNING


def test_compat_enum_int_value_works_with_set_level() -> None:
    logger = logging.getLogger("compat.test")
    validated_int = _Model(level=20).level
    logger.setLevel(validated_int)
    assert logger.level == logging.INFO
