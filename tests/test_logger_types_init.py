import sys

import pytest

import pydantic_logger._logger_types

_PICOLOGGING_SUPPORTED = sys.version_info[:2] <= (3, 12)
_ELIOT_SUPPORTED = sys.version_info[:2] >= (3, 10)


def test_getattr_raises_for_unknown_in_package() -> None:
    with pytest.raises(AttributeError):
        getattr(pydantic_logger, "NonExistentLogger")  # ignore


def test_getattr_raises_for_unknown_in_logger_types() -> None:
    with pytest.raises(AttributeError):
        getattr(pydantic_logger._logger_types, "NonExistentLogger")  # ignore


def test_logger_types_getattr_loguru() -> None:
    assert (
        pydantic_logger._logger_types.PydanticLoguruLogger
        is pydantic_logger.PydanticLoguruLogger
    )


def test_logger_types_getattr_structlog() -> None:
    assert (
        pydantic_logger._logger_types.PydanticStructlogLogger
        is pydantic_logger.PydanticStructlogLogger
    )


def test_logger_types_getattr_logbook() -> None:
    assert (
        pydantic_logger._logger_types.PydanticLogbookLogger
        is pydantic_logger.PydanticLogbookLogger
    )


@pytest.mark.skipif(
    not _PICOLOGGING_SUPPORTED,
    reason="picologging supports Python 3.7-3.12",
)
def test_logger_types_getattr_picologging() -> None:
    assert (
        pydantic_logger._logger_types.PydanticPicologgingLogger
        is pydantic_logger.PydanticPicologgingLogger
    )


@pytest.mark.skipif(
    _PICOLOGGING_SUPPORTED,
    reason="picologging supports Python 3.7-3.12",
)
def test_logger_types_getattr_picologging_raises_on_unsupported_python() -> (
    None
):
    with pytest.raises(ImportError, match="picologging supports Python"):
        pydantic_logger._logger_types.PydanticPicologgingLogger


@pytest.mark.skipif(
    not _ELIOT_SUPPORTED,
    reason="eliot requires Python 3.10+",
)
def test_logger_types_getattr_eliot() -> None:
    assert (
        pydantic_logger._logger_types.PydanticEliotLogger
        is pydantic_logger.PydanticEliotLogger
    )


@pytest.mark.skipif(
    _ELIOT_SUPPORTED,
    reason="eliot requires Python 3.10+",
)
def test_logger_types_getattr_eliot_raises_on_unsupported_python() -> None:
    with pytest.raises(ImportError, match="eliot requires Python"):
        pydantic_logger._logger_types.PydanticEliotLogger


def test_logger_types_getattr_logfire() -> None:
    assert (
        pydantic_logger._logger_types.PydanticLogfireLogger
        is pydantic_logger.PydanticLogfireLogger
    )
