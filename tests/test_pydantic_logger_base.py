import inspect
import logging
import os
import typing
from types import FrameType
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import structlog
from pydantic import ValidationError

import pydantic_logger._pydantic_logger_base as base_mod
from pydantic_logger import PydanticLogger
from pydantic_logger import PydanticLoggerBase


def test_default_name_is_caller_module() -> None:
    logger = PydanticLogger()
    assert logger.name == "tests.test_pydantic_logger_base"


def test_default_name_raises_when_no_valid_frame() -> None:
    with patch.object(inspect, "currentframe", return_value=None):
        with pytest.raises(
            ValueError, match="Could not determine caller module name"
        ):
            PydanticLogger()


def test_default_name_skips_non_string_module_names() -> None:
    mock_frame_with_non_string = MagicMock(spec=FrameType)
    mock_frame_with_non_string.f_globals = {"__name__": 123}
    mock_frame_with_non_string.f_back = None

    with patch.object(
        inspect, "currentframe", return_value=mock_frame_with_non_string
    ):
        with pytest.raises(
            ValueError, match="Could not determine caller module name"
        ):
            PydanticLogger()


def test_default_level_is_none() -> None:
    assert PydanticLogger().level is None


def test_logger_field_is_logging_logger() -> None:
    assert isinstance(PydanticLogger().logger, logging.Logger)


def test_custom_name() -> None:
    logger = PydanticLogger(name="my.logger")
    assert logger.name == "my.logger"
    assert logger.logger.name == "my.logger"


def test_level_sets_logger_level() -> None:
    logger = PydanticLogger(name="level.test.int", level=logging.DEBUG)
    assert logger.logger.level == logging.DEBUG


def test_level_string_sets_logger_level() -> None:
    logger = PydanticLogger(name="level.test.str", level="WARNING")
    assert logger.logger.level == logging.WARNING


def test_level_none_does_not_override_logger_level() -> None:
    underlying = logging.getLogger("level.test.none")
    underlying.setLevel(logging.ERROR)
    logger = PydanticLogger(name="level.test.none", level=None)
    assert logger.logger.level == logging.ERROR


def test_invalid_level_raises() -> None:
    with pytest.raises(ValidationError):
        PydanticLogger(level="INVALID_LEVEL")


def test_logger_excluded_from_serialization() -> None:
    data = PydanticLogger(name="serial.test").model_dump()
    assert "logger" not in data


def test_extra_fields_are_ignored() -> None:
    logger = PydanticLogger(name="x", unknown_field=True)
    assert not hasattr(logger, "unknown_field")  # ignore


def test_frozen_prevents_name_mutation() -> None:
    logger = PydanticLogger(name="frozen.test")
    with pytest.raises(ValidationError):
        logger.name = "other"  # type: ignore[misc]


def test_frozen_prevents_level_mutation() -> None:
    logger = PydanticLogger(name="frozen.level")
    with pytest.raises(ValidationError):
        logger.level = "DEBUG"  # type: ignore[misc,assignment]


@pytest.fixture
def logger_with_mock():
    mock_logger = MagicMock(spec=logging.Logger)
    pydantic_logger = PydanticLogger(name="method.test", logger=mock_logger)
    return pydantic_logger, mock_logger


def test_debug_delegates(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.debug("msg", "arg", key="val")
    mock_logger.debug.assert_called_once_with("msg", "arg", key="val")


def test_info_delegates(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.info("msg")
    mock_logger.info.assert_called_once_with("msg")


def test_warning_delegates(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.warning("msg")
    mock_logger.warning.assert_called_once_with("msg")


def test_error_delegates(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.error("msg")
    mock_logger.error.assert_called_once_with("msg")


def test_critical_delegates(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.critical("msg")
    mock_logger.critical.assert_called_once_with("msg")


def test_exception_delegates(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.exception("msg")
    mock_logger.exception.assert_called_once_with("msg")


def test_log_delegates_with_level(logger_with_mock) -> None:
    pydantic_logger, mock_logger = logger_with_mock
    pydantic_logger.log(logging.WARNING, "msg")
    mock_logger.log.assert_called_once_with(logging.WARNING, "msg")


def test_stack_level_injected_into_kwargs() -> None:
    mock_logger = MagicMock(spec=logging.Logger)
    pydantic_logger = PydanticLogger(
        name="stack_level.test", stack_level=2, logger=mock_logger
    )
    pydantic_logger.info("msg")
    mock_logger.info.assert_called_once_with("msg", stack_level=2)


def test_stack_level_not_overridden_when_caller_provides_it() -> None:
    mock_logger = MagicMock(spec=logging.Logger)
    pydantic_logger = PydanticLogger(
        name="stack_level.override.test", stack_level=2, logger=mock_logger
    )
    pydantic_logger.info("msg", stack_level=5)
    mock_logger.info.assert_called_once_with("msg", stack_level=5)


def test_stack_level_read_from_env_var() -> None:
    with patch.dict(os.environ, {"PYDANTIC_LOGGER_STACK_LEVEL": "3"}):
        logger = PydanticLogger(name="env.stack_level")
    assert logger.stack_level == 3


def test_stack_level_env_var_zero_raises() -> None:
    with patch.dict(os.environ, {"PYDANTIC_LOGGER_STACK_LEVEL": "0"}):
        with pytest.raises(ValueError):
            PydanticLogger(name="env.stack_level.invalid")


def test_invalid_logger_passed_raises() -> None:
    with pytest.raises(ValueError):
        PydanticLogger(name="bad.logger", logger=object())  # type: ignore[arg-type]


def test_logger_type_validator_raises_when_multiple_types() -> None:
    class _ALogger(PydanticLoggerBase[logging.Logger]):  # type: ignore[type-arg]
        def _create_logger(self) -> logging.Logger:
            return logging.getLogger(self.name)

    class _BLogger(PydanticLoggerBase[structlog.PrintLogger]):  # type: ignore[type-arg]
        def _create_logger(self) -> structlog.PrintLogger:
            return structlog.PrintLogger()

    class _MultiLogger(_ALogger, _BLogger):  # type: ignore[misc]
        def _create_logger(self) -> logging.Logger:
            return logging.getLogger(self.name)

    parameterized_parents = [
        PydanticLoggerBase[logging.Logger],
        PydanticLoggerBase[structlog.PrintLogger],
    ]
    with patch.object(
        base_mod, "_get_unique_bases", return_value=iter(parameterized_parents)
    ):
        with pytest.raises(ValueError, match="more than one"):
            _MultiLogger._logger_type_validator(logging.getLogger("x"))


def test_logger_type_validator_skips_non_loggertype_arg() -> None:
    class _SkipLogger(PydanticLoggerBase[logging.Logger]):  # type: ignore[type-arg]
        def _create_logger(self) -> logging.Logger:
            return logging.getLogger(self.name)

    OtherVar = typing.TypeVar("OtherVar")

    class _FakeBase(PydanticLoggerBase[logging.Logger]):  # type: ignore[type-arg]
        def _create_logger(self) -> logging.Logger:
            return logging.getLogger(self.name)

    _FakeBase.__orig_bases__ = (typing.Generic[OtherVar],)  # type: ignore[attr-defined]
    _FakeBase.__pydantic_generic_metadata__ = {"args": (str,)}  # type: ignore[attr-defined]

    real_base = PydanticLoggerBase[logging.Logger]
    with patch.object(
        base_mod,
        "_get_unique_bases",
        return_value=iter([_FakeBase, real_base]),
    ):
        result = _SkipLogger._logger_type_validator(
            logging.getLogger("skip.test")
        )
    assert isinstance(result, logging.Logger)
