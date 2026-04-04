import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from typing import ClassVar, Literal

class _StreamHandlerConfig(BaseModel):
    model_config: ClassVar[ConfigDict]
    stream: Literal["stdout", "stderr"]
    def build(self) -> logging.Handler: ...

class _FileHandlerConfig(BaseModel):
    model_config: ClassVar[ConfigDict]
    path: Path
    def build(self) -> logging.Handler: ...

class _LoggingConfig(BaseModel):
    model_config: ClassVar[ConfigDict]
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    format: str
    handlers: tuple[_StreamHandlerConfig | _FileHandlerConfig, ...]
    def apply(self) -> None: ...
