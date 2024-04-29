#!/usr/bin/env bash
# Reset to a base commit, optionally apply a test patch, and run the verifier suite.
# Usage: ./validate-at-base.sh [base_commit] [test_patch]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

BASE_COMMIT="${1:-HEAD}"
TEST_PATCH="${2:-}"

if ! git rev-parse --verify "$BASE_COMMIT" >/dev/null 2>&1; then
  echo "ERROR: unknown base commit: $BASE_COMMIT" >&2
  exit 1
fi

echo "==> Checking out base commit: $BASE_COMMIT"
git stash push -u -m "validate-at-base-$(date +%s)" 2>/dev/null || true
git checkout "$BASE_COMMIT"

if [[ -n "$TEST_PATCH" && -f "$TEST_PATCH" ]]; then
  echo "==> Applying test patch: $TEST_PATCH"
  git apply "$TEST_PATCH"
fi

echo "==> Installing test dependencies"
python3 -m pip install -q -r requirements-core.txt

echo "==> Running pytest"
python3 -m pytest tests/ -q --tb=short

echo "==> validate-at-base: PASS"
