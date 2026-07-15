import json
import logging
import time
import traceback
import urllib.request
from logging import Handler
from logging import LogRecord
from typing import TypedDict

from pydantic_logger._handlers._github_auto_fix._settings import (
    _GitHubAutoFixSettings as GitHubAutoFixSettings,
)


class _ClientPayload(TypedDict):
    service: str
    location: str
    file_path: str
    error_type: str
    message: str
    traceback: str


class _GitHubAutoFixHandler(Handler):
    """Ring 4 (Infrastructure) handler that fires a GitHub repository_dispatch
    event for each unique (file, line) ERROR so the auto-fix workflow can open
    a Claude Code-proposed PR.  Only instantiated when GITHUB_DISPATCH_TOKEN
    and GITHUB_REPO are both set.  Sends full error context (not redacted) to
    a private GitHub API endpoint.

    Paired with the following workflow (e.g. .github/workflows/auto-fix-log-error.yml)::

        name: Auto-Fix Log Error

        # repository_dispatch is an explicit API-triggered event (not push/PR/schedule).
        # Prohibited automatic triggers are push, pull_request, schedule --- not this.
        # Added with explicit user approval; see .github/workflows/README.md for policy.
        on:
          repository_dispatch:
            types: [log-error-fix]

        permissions:
          contents: write
          pull-requests: write

        concurrency:
          # Serialise per error site; prevents two rapid dispatches opening duplicate PRs.
          group: auto-fix-${{ github.event.client_payload.location }}
          cancel-in-progress: false

        jobs:
          auto-fix:
            runs-on: ubuntu-latest

            steps:
              - uses: actions/checkout@v4
                with:
                  ref: dev
                  fetch-depth: 0

              - name: Build prompt
                id: prompt
                env:
                  FILE_PATH: ${{ github.event.client_payload.file_path }}
                  ERROR_TYPE: ${{ github.event.client_payload.error_type }}
                  SERVICE: ${{ github.event.client_payload.service }}
                  LOCATION: ${{ github.event.client_payload.location }}
                  MESSAGE: ${{ github.event.client_payload.message }}
                  TRACEBACK: ${{ github.event.client_payload.traceback }}
                run: |
                  python3 - << 'PY'
                  import os

                  prompt = (
                      "Fix the following Python runtime error in the Enso backend.\n"
                      "Apply the minimal change required. Do not refactor unrelated code,\n"
                      "add comments, or create new files unless the fix requires it.\n\n"
                      f"Focus on: {os.environ['FILE_PATH']}\n\n"
                      f"Error type:  {os.environ['ERROR_TYPE']}\n"
                      f"Service:     {os.environ['SERVICE']}\n"
                      f"Location:    {os.environ['LOCATION']}\n\n"
                      "Error message:\n"
                      f"{os.environ['MESSAGE']}\n\n"
                      "Traceback:\n"
                      f"{os.environ['TRACEBACK']}\n"
                  )

                  # Write as multiline GITHUB_OUTPUT value (safe for special chars).
                  with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                      fh.write("text<<PROMPT_EOF\n")
                      fh.write(prompt)
                      fh.write("\nPROMPT_EOF\n")
                  PY

              - uses: grll/claude-code-action@beta
                with:
                  use_oauth: "true"
                  claude_access_token: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
                  claude_refresh_token: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
                  claude_expires_at: ${{ secrets.CLAUDE_EXPIRES_AT }}
                  secrets_admin_pat: ${{ secrets.SECRETS_ADMIN_PAT }}
                  direct_prompt: ${{ steps.prompt.outputs.text }}
                  base_branch: dev
                  branch_prefix: auto-fix/
                  timeout_minutes: "30"
    """

    _DISPATCH_URL = "https://api.github.com/repos/{repo}/dispatches"
    _MAX_MESSAGE_CHARS = 2_000
    _MAX_TRACEBACK_CHARS = 8_000
    _REQUEST_TIMEOUT = 5.0

    def __init__(self, settings: GitHubAutoFixSettings) -> None:
        super().__init__(level=logging.ERROR)
        self._token = settings.github_dispatch_token
        self._repo = settings.github_repo
        self._same_message_sent_interval_seconds = (
            settings.same_message_sent_interval_seconds
        )
        self._recently_sent: dict[tuple[str, int], float] = {}

    @staticmethod
    def _get_cache_key(record: LogRecord) -> tuple[str, int]:
        return record.pathname, record.lineno

    def _build_client_payload(self, record: LogRecord) -> _ClientPayload:
        try:
            message = record.getMessage()
        except Exception:
            message = str(record.msg)

        traceback_text = ""
        if record.exc_info and record.exc_info[0] is not None:
            traceback_text = "".join(
                traceback.format_exception(*record.exc_info)
            )
            if len(traceback_text) > self._MAX_TRACEBACK_CHARS:
                traceback_text = (
                    "...(truncated)\n"
                    + traceback_text[-self._MAX_TRACEBACK_CHARS :]
                )

        error_type = (
            record.exc_info[0].__name__
            if record.exc_info and record.exc_info[0] is not None
            else record.levelname
        )

        return _ClientPayload(
            service=record.name.split(".")[0],
            location=f"{record.pathname}:{record.lineno}",
            file_path=record.pathname,
            error_type=error_type,
            message=message[: self._MAX_MESSAGE_CHARS],
            traceback=traceback_text,
        )

    def emit(self, record: LogRecord) -> None:
        try:
            key = self._get_cache_key(record)
            now = time.monotonic()

            assert self.lock is not None
            with self.lock:
                last_sent_at = self._recently_sent.get(key) or 0
                if (
                    now - last_sent_at
                    < self._same_message_sent_interval_seconds
                ):
                    return

                payload = {
                    "event_type": "log-error-fix",
                    "client_payload": self._build_client_payload(record),
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url=self._DISPATCH_URL.format(repo=self._repo),
                    data=data,
                    headers={
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {self._token}",
                        "Content-Type": "application/json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(
                    req, timeout=self._REQUEST_TIMEOUT
                ):
                    pass

                self._recently_sent[key] = now

                expired_keys = [
                    k
                    for k, sent_at in self._recently_sent.items()
                    if now - sent_at
                    >= self._same_message_sent_interval_seconds
                ]
                for k in expired_keys:
                    del self._recently_sent[k]
        except Exception:
            self.handleError(record)
