#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

REPO_DIR="${TMP_ROOT}/repo"
SKILLS_DIR="${TMP_ROOT}/skills"
PROJECT_DIR="${TMP_ROOT}/project"

mkdir -p "${PROJECT_DIR}"

bash "${ROOT}/scripts/install.sh" \
  --source "${ROOT}" \
  --repo-dir "${REPO_DIR}" \
  --skills-dir "${SKILLS_DIR}" \
  --project-dir "${PROJECT_DIR}" \
  --yes \
  --force

if [ ! -d "${REPO_DIR}/skills" ]; then
  echo "repo dir was not created correctly"
  exit 1
fi

if [ -e "${REPO_DIR}/.codex" ]; then
  echo "suite repo copy should not contain repo-local .codex"
  exit 1
fi

if [ ! -L "${SKILLS_DIR}/forgeloop" ]; then
  echo "skills link was not created"
  exit 1
fi

TARGET="$(readlink "${SKILLS_DIR}/forgeloop")"
TARGET_REAL="$(cd "${TARGET}" && pwd -P)"
EXPECTED_REAL="$(cd "${REPO_DIR}/skills" && pwd -P)"
if [ "${TARGET_REAL}" != "${EXPECTED_REAL}" ]; then
  echo "skills link points to unexpected target: ${TARGET}"
  exit 1
fi

for agent in planner design_reviewer gap_reviewer plan_reviewer coder task_reviewer milestone_reviewer initiative_reviewer; do
  if [ ! -f "${PROJECT_DIR}/.codex/agents/${agent}.toml" ]; then
    echo "project agent was not installed: ${agent}"
    exit 1
  fi
done

DOCTOR_OUTPUT="$(bash "${ROOT}/scripts/install.sh" \
  --doctor \
  --source "${ROOT}" \
  --repo-dir "${REPO_DIR}" \
  --skills-dir "${SKILLS_DIR}" \
  --project-dir "${PROJECT_DIR}")"

printf '%s\n' "${DOCTOR_OUTPUT}" | grep -q "source kind: local-path"
printf '%s\n' "${DOCTOR_OUTPUT}" | grep -q "skills link:"
printf '%s\n' "${DOCTOR_OUTPUT}" | grep -q "project agents: present"

echo "install script smoke test passed"
