#!/usr/bin/env bash
set -euo pipefail

pytest --cov=backend --cov-report=term-missing
ruff check .
