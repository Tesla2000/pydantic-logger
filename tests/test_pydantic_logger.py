import inspect
import logging
from types import FrameType
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from pydantic_logger import PydanticLogger
from pydantic_logger._pydantic_logger import _create_logger
from pydantic_logger._pydantic_logger import _get_caller_module_name


def test_create_logger_raises_on_missing_keys() -> None:
    with pytest.raises(ValueError):
        _create_logger({})


def test_default_name_is_caller_module() -> None:
    logger = PydanticLogger()
    assert logger.name == "tests.test_pydantic_logger"


def test_get_caller_module_name_returns_module_name() -> None:
    module_name = _get_caller_module_name()
    assert module_name == "tests.test_pydantic_logger"


def test_get_caller_module_name_raises_when_no_valid_frame() -> None:
    with patch.object(inspect, "currentframe", return_value=None):
        with pytest.raises(
            ValueError, match="Could not determine caller module name"
        ):
            _get_caller_module_name()


def test_get_caller_module_name_skips_non_string_module_names() -> None:
    mock_frame_with_non_string = MagicMock(spec=FrameType)
    mock_frame_with_non_string.f_globals = {"__name__": 123}
    mock_frame_with_non_string.f_back = None

    with patch.object(
        inspect, "currentframe", return_value=mock_frame_with_non_string
    ):
        with pytest.raises(
            ValueError, match="Could not determine caller module name"
        ):
            _get_caller_module_name()


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
    pydantic_logger = PydanticLogger(name="method.test")
    object.__setattr__(pydantic_logger, "logger", mock_logger)
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


def test_stacklevel_injected_into_kwargs() -> None:
    mock_logger = MagicMock(spec=logging.Logger)
    pydantic_logger = PydanticLogger(name="stacklevel.test", stacklevel=2)
    object.__setattr__(pydantic_logger, "logger", mock_logger)
    pydantic_logger.info("msg")
    mock_logger.info.assert_called_once_with("msg", stacklevel=2)


def test_stacklevel_not_overridden_when_caller_provides_it() -> None:
    mock_logger = MagicMock(spec=logging.Logger)
    pydantic_logger = PydanticLogger(
        name="stacklevel.override.test", stacklevel=2
    )
    object.__setattr__(pydantic_logger, "logger", mock_logger)
    pydantic_logger.info("msg", stacklevel=5)
    mock_logger.info.assert_called_once_with("msg", stacklevel=5)
