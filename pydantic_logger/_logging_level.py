from enum import StrEnum
from typing import Annotated
from typing import Union

from pydantic import BeforeValidator


class _LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


def _conv_str(data: object) -> object:
    if isinstance(data, str):
        return data.upper()
    return data


_LoggingLevelAnnotation = Annotated[
    Union[_LoggingLevel, int], BeforeValidator(_conv_str)
]
