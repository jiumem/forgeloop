#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="${PLUGIN_ROOT}/agents"
CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"
PROJECT_DIR=""
TARGET_DIR=""

usage() {
  cat <<'EOF'
Usage: materialize-agents.sh [--project-dir <path>]

Copies Forgeloop custom agent manifests into Codex custom agent storage.

Default target:
  $CODEX_HOME/agents or ~/.codex/agents

Override target:
  --project-dir <path>  -> <path>/.codex/agents
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-dir)
      if [ "$#" -lt 2 ] || [ -z "${2:-}" ]; then
        printf 'Missing value for --project-dir\n' >&2
        usage >&2
        exit 1
      fi
      PROJECT_DIR="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ ! -d "${SOURCE_DIR}" ]; then
  printf 'Plugin agent source directory not found: %s\n' "${SOURCE_DIR}" >&2
  exit 1
fi

if [ -n "${PROJECT_DIR}" ]; then
  if [ ! -d "${PROJECT_DIR}" ]; then
    printf 'Project directory not found: %s\n' "${PROJECT_DIR}" >&2
    exit 1
  fi
  TARGET_DIR="${PROJECT_DIR}/.codex/agents"
else
  TARGET_DIR="${CODEX_HOME_DIR}/agents"
fi

mkdir -p "${TARGET_DIR}"
cp "${SOURCE_DIR}"/*.toml "${TARGET_DIR}/"
printf 'Materialized Forgeloop agents into %s\n' "${TARGET_DIR}"
