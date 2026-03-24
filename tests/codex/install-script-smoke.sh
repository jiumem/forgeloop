#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

REPO_DIR="${TMP_ROOT}/repo"
SKILLS_DIR="${TMP_ROOT}/skills"

bash "${ROOT}/scripts/install.sh" \
  --source "${ROOT}" \
  --repo-dir "${REPO_DIR}" \
  --skills-dir "${SKILLS_DIR}" \
  --yes \
  --force

if [ ! -d "${REPO_DIR}/skills" ]; then
  echo "repo dir was not created correctly"
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

DOCTOR_OUTPUT="$(bash "${ROOT}/scripts/install.sh" \
  --doctor \
  --source "${ROOT}" \
  --repo-dir "${REPO_DIR}" \
  --skills-dir "${SKILLS_DIR}")"

printf '%s\n' "${DOCTOR_OUTPUT}" | grep -q "source kind: local-path"
printf '%s\n' "${DOCTOR_OUTPUT}" | grep -q "skills link:"

echo "install script smoke test passed"
