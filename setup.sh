#!/usr/bin/env bash
set -e

uv sync
git init
git add .
git commit -m "initial commit"
pre-commit install --hook-type pre-commit --hook-type pre-push
pre-commit autoupdate
