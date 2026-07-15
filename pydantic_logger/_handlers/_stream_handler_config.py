import logging
import sys
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
