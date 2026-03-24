#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SOURCE="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_REPO_DIR="${HOME}/.codex/forgeloop"
DEFAULT_SKILLS_DIR="${HOME}/.codex/skills"
DEFAULT_LINK_NAME="forgeloop"

SOURCE="${DEFAULT_SOURCE}"
REPO_DIR="${DEFAULT_REPO_DIR}"
SKILLS_DIR="${DEFAULT_SKILLS_DIR}"
LINK_NAME="${DEFAULT_LINK_NAME}"
REF=""
FORCE=0
DRY_RUN=0
ASSUME_YES=0
VERBOSE=0
DOCTOR=0

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [options]

Options:
  --source <path-or-git-url>  Install source. Defaults to the current checkout.
  --repo-dir <path>           Managed repository location. Default: ~/.codex/forgeloop
  --skills-dir <path>         Codex skills directory. Default: ~/.codex/skills
  --link-name <name>          Symlink name inside the skills directory. Default: forgeloop
  --ref <git-ref>             Branch, tag, or commit when --source is a git URL.
  --force                     Replace existing checkout/symlink when needed.
  --dry-run                   Print actions without changing the filesystem.
  --yes                       Skip confirmation prompts.
  --verbose                   Print extra logging.
  --doctor                    Check inputs and installation state without changing anything.
  --help                      Show this help text.
EOF
}

log() {
  printf '%s\n' "$*"
}

debug() {
  if [ "${VERBOSE}" -eq 1 ]; then
    printf '[debug] %s\n' "$*"
  fi
}

run() {
  if [ "${DRY_RUN}" -eq 1 ]; then
    printf '[dry-run] %s\n' "$*"
    return 0
  fi
  debug "$*"
  "$@"
}

is_git_url() {
  case "$1" in
    http://*|https://*|ssh://*|git@*|*.git)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

confirm() {
  local prompt="$1"
  if [ "${ASSUME_YES}" -eq 1 ]; then
    return 0
  fi
  printf '%s [y/N] ' "$prompt" >&2
  read -r answer
  case "$answer" in
    y|Y|yes|YES)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

canonical_path() {
  local target="$1"
  if [ -e "$target" ] || [ -L "$target" ]; then
    (cd "$target" 2>/dev/null && pwd -P) || (cd "$(dirname "$target")" && printf '%s/%s\n' "$(pwd -P)" "$(basename "$target")")
  else
    (cd "$(dirname "$target")" && printf '%s/%s\n' "$(pwd -P)" "$(basename "$target")")
  fi
}

remove_path() {
  local target="$1"
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    return 0
  fi
  if [ "${DRY_RUN}" -eq 1 ]; then
    printf '[dry-run] remove %s\n' "$target"
    return 0
  fi
  python3 - "$target" <<'PY'
import os
import shutil
import sys

path = sys.argv[1]
if os.path.islink(path) or os.path.isfile(path):
    os.unlink(path)
elif os.path.isdir(path):
    shutil.rmtree(path)
PY
}

ensure_dir() {
  local target="$1"
  run mkdir -p "$target"
}

sync_local_source() {
  local source_path="$1"
  local target_path="$2"
  local source_real target_real parent

  source_real="$(canonical_path "$source_path")"
  target_real="$(canonical_path "$target_path")"

  if [ "${source_real}" = "${target_real}" ]; then
    log "using local checkout: ${source_real}"
    printf '%s\n' "${source_real}"
    return 0
  fi

  if [ -e "$target_path" ] || [ -L "$target_path" ]; then
    if [ "${FORCE}" -ne 1 ]; then
      log "repo dir already exists: ${target_path}"
      log "re-run with --force to replace it"
      exit 1
    fi
    confirm "replace existing repo dir at ${target_path}?" || exit 1
    remove_path "$target_path"
  fi

  parent="$(dirname "$target_path")"
  ensure_dir "$parent"

  run cp -R "$source_path" "$target_path"

  printf '%s\n' "$(canonical_path "$target_path")"
}

sync_remote_source() {
  local source_url="$1"
  local target_path="$2"
  local ref="$3"

  ensure_dir "$(dirname "$target_path")"

  if [ ! -d "${target_path}/.git" ]; then
    if [ -e "$target_path" ] || [ -L "$target_path" ]; then
      if [ "${FORCE}" -ne 1 ]; then
        log "repo dir exists but is not a git checkout: ${target_path}"
        log "re-run with --force to replace it"
        exit 1
      fi
      confirm "replace existing path at ${target_path}?" || exit 1
      remove_path "$target_path"
    fi
    run git clone "$source_url" "$target_path"
  else
    run git -C "$target_path" fetch --all --tags
  fi

  if [ -n "$ref" ]; then
    run git -C "$target_path" checkout "$ref"
  else
    local branch
    branch="$(git -C "$target_path" symbolic-ref --quiet --short HEAD || true)"
    if [ -n "$branch" ]; then
      run git -C "$target_path" pull --ff-only origin "$branch"
    fi
  fi

  printf '%s\n' "$(canonical_path "$target_path")"
}

install_link() {
  local repo_path="$1"
  local skills_path="$2"
  local link_name="$3"
  local target="${skills_path}/${link_name}"
  local source="${repo_path}/skills"

  if [ ! -d "$source" ]; then
    log "skills directory not found: ${source}"
    exit 1
  fi

  ensure_dir "$skills_path"

  if [ -L "$target" ]; then
    local current
    current="$(readlink "$target")"
    if [ "$current" = "$source" ]; then
      log "skills link already correct: ${target}"
      return 0
    fi
    if [ "${FORCE}" -ne 1 ]; then
      log "skills link already exists: ${target}"
      log "re-run with --force to replace it"
      exit 1
    fi
    confirm "replace existing symlink at ${target}?" || exit 1
    remove_path "$target"
  elif [ -e "$target" ]; then
    if [ "${FORCE}" -ne 1 ]; then
      log "path already exists and is not a symlink: ${target}"
      log "re-run with --force to replace it"
      exit 1
    fi
    confirm "replace existing path at ${target}?" || exit 1
    remove_path "$target"
  fi

  run ln -sfn "$source" "$target"
  log "linked ${target} -> ${source}"
}

doctor() {
  local source_kind
  local resolved_source
  if is_git_url "$SOURCE"; then
    source_kind="git-url"
    resolved_source="$SOURCE"
  else
    source_kind="local-path"
    resolved_source="$(canonical_path "$SOURCE")"
  fi

  log "doctor report"
  log "  source kind: ${source_kind}"
  log "  source: ${resolved_source}"
  log "  repo dir: $(canonical_path "$REPO_DIR")"
  log "  skills dir: $(canonical_path "$SKILLS_DIR")"
  log "  link name: ${LINK_NAME}"
  log "  git available: $(command -v git >/dev/null && printf yes || printf no)"

  if [ -d "${REPO_DIR}/skills" ]; then
    log "  repo skills dir: present"
  else
    log "  repo skills dir: missing"
  fi

  if [ -L "${SKILLS_DIR}/${LINK_NAME}" ]; then
    log "  skills link: $(readlink "${SKILLS_DIR}/${LINK_NAME}")"
  elif [ -e "${SKILLS_DIR}/${LINK_NAME}" ]; then
    log "  skills link path exists but is not a symlink"
  else
    log "  skills link: missing"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --repo-dir)
      REPO_DIR="$2"
      shift 2
      ;;
    --skills-dir)
      SKILLS_DIR="$2"
      shift 2
      ;;
    --link-name)
      LINK_NAME="$2"
      shift 2
      ;;
    --ref)
      REF="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --yes)
      ASSUME_YES=1
      shift
      ;;
    --verbose)
      VERBOSE=1
      shift
      ;;
    --doctor)
      DOCTOR=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      log "unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  log "git is required"
  exit 1
fi

if [ "${DOCTOR}" -eq 1 ]; then
  doctor
  exit 0
fi

if ! is_git_url "$SOURCE" && [ ! -d "$SOURCE" ]; then
  log "local source path not found: ${SOURCE}"
  exit 1
fi

if is_git_url "$SOURCE"; then
  RESOLVED_REPO_DIR="$(sync_remote_source "$SOURCE" "$REPO_DIR" "$REF")"
else
  RESOLVED_REPO_DIR="$(sync_local_source "$SOURCE" "$REPO_DIR")"
fi

install_link "$RESOLVED_REPO_DIR" "$SKILLS_DIR" "$LINK_NAME"

log "install complete"
log "  repo: ${RESOLVED_REPO_DIR}"
log "  skills link: ${SKILLS_DIR}/${LINK_NAME}"
log "restart Codex to pick up new skills"
