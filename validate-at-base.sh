#!/usr/bin/env bash
# Run the test suite at a specific git revision (regression / bisect helper).
# Usage: ./validate-at-base.sh [commit] [optional_patch]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

BASE_COMMIT="${1:-HEAD}"
TEST_PATCH="${2:-}"
ORIG_REF="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
ORIG_SHA="$(git rev-parse HEAD)"
STASHED=0

cleanup() {
  cd "$ROOT"
  if git rev-parse --verify "$ORIG_SHA" >/dev/null 2>&1; then
    git checkout "$ORIG_SHA" >/dev/null 2>&1 || git checkout "$ORIG_REF" >/dev/null 2>&1 || true
  fi
  if [[ "$STASHED" -eq 1 ]]; then
    git stash pop >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

if ! git rev-parse --verify "$BASE_COMMIT" >/dev/null 2>&1; then
  echo "ERROR: unknown commit: $BASE_COMMIT" >&2
  exit 1
fi

echo "==> Stashing working tree"
if git stash push -u -m "validate-at-base-$(date +%s)" >/dev/null 2>&1; then
  STASHED=1
fi

echo "==> Checking out: $BASE_COMMIT"
git checkout "$BASE_COMMIT"

if [[ -n "$TEST_PATCH" && -f "$TEST_PATCH" ]]; then
  echo "==> Applying patch: $TEST_PATCH"
  git apply --check "$TEST_PATCH"
  git apply "$TEST_PATCH"
fi

echo "==> Installing dependencies"
python3 -m pip install -q -r requirements-core.txt

echo "==> Running pytest"
python3 -m pytest tests/ -q --tb=short

echo "==> validate-at-base: PASS"
