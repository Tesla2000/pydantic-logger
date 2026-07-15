from typing import ClassVar

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PositiveFloat


class _GitHubAutoFixSettings(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    github_dispatch_token: str
    github_repo: str
    same_message_sent_interval_seconds: PositiveFloat = 300.0
