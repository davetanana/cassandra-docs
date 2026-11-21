#!/usr/bin/env bash
# Stop every container (all profiles) and DELETE all volumes and staged files. The test cluster is disposable.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
"${COMPOSE[@]}" --profile replace --profile dc2 --profile s3 down -v --remove-orphans
# shared/ is written by root inside the containers, so clean it from a container.
docker run --rm -v "$ENV_DIR/shared:/shared" "${CASSANDRA_IMAGE:-cassandra:5.0}" bash -c 'rm -rf /shared/* 2>/dev/null' >/dev/null 2>&1 || true
