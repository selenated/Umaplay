#!/usr/bin/env bash

set -euo pipefail

PORT="${1:-8001}"
export TEMPLATE_MATCH_TIMEOUT=300

echo "Starting server on port ${PORT}..."
exec uvicorn server.main_inference:app --host 0.0.0.0 --port "${PORT}"
