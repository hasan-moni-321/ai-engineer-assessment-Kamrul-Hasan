#!/usr/bin/env bash
set -euo pipefail

python -m backend.ingestion.ingest \
  --pdf "${1:-data/docker_kubernetes_dataset.pdf}"
