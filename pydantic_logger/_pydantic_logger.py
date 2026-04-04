import logging
import uuid
from logging import Logger
from typing import Any
from typing import ClassVar
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import InstanceOf


def _create_logger(validated_data: dict[str, Any]) -> Logger:
    if "name" not in validated_data or "level" not in validated_data:
        raise ValueError(
            f"Logger name or level not in validated data {validated_data}"
        )
    logger = logging.getLogger(validated_data["name"])
    logger.setLevel(validated_data["level"])
    return logger


class _PydanticLogger(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    level: Optional[
        Literal[
            50,
            40,
            30,
            20,
            10,
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
            "NOTSET",
        ]
    ] = None
    name: str = Field(default_factory=lambda: str(uuid.uuid4()))
    logger: InstanceOf[Logger] = Field(
        default_factory=_create_logger, exclude=True
    )

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.exception(msg, *args, **kwargs)

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.log(level, msg, *args, **kwargs)
