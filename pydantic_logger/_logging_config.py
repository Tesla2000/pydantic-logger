import logging
import sys
from pathlib import Path
from typing import ClassVar
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict


class _StreamHandlerConfig(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    stream: Literal["stdout", "stderr"] = "stdout"

    def build(self) -> logging.Handler:
        return logging.StreamHandler(
            sys.stdout if self.stream == "stdout" else sys.stderr
        )


class _FileHandlerConfig(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    path: Path

    def build(self) -> logging.Handler:
        return logging.FileHandler(str(self.path))


class _LoggingConfig(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handlers: tuple[_StreamHandlerConfig | _FileHandlerConfig, ...] = (
        _StreamHandlerConfig(),
    )

    def apply(self) -> None:
        formatter = logging.Formatter(self.format)
        handlers = [h.build() for h in self.handlers]
        for handler in handlers:
            handler.setFormatter(formatter)
        logging.basicConfig(level=self.level, handlers=handlers)
