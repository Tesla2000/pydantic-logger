import logging
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel
from pydantic import ConfigDict


class _FileHandlerConfig(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    path: Path

    def build(self) -> logging.Handler:
        return logging.FileHandler(str(self.path))
