#!/usr/bin/env bash
# Local CI sanity checks before push or release.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

fail() { echo "FAIL: $1" >&2; FAIL=1; }
pass() { echo "PASS: $1"; }

if [[ ! -f Dockerfile ]]; then
  fail "Dockerfile missing"
else
  pass "Dockerfile exists"
  size=$(wc -c < Dockerfile | tr -d ' ')
  lines=$(wc -l < Dockerfile | tr -d ' ')
  runs=$(grep -cE '^[[:space:]]*RUN[[:space:]]' Dockerfile || true)
  [[ "$size" -le 20480 ]] || fail "Dockerfile ${size}B exceeds 20KB"
  [[ "$lines" -le 200 ]] || fail "Dockerfile ${lines} lines exceeds 200"
  [[ "$runs" -le 30 ]] || fail "Dockerfile has ${runs} RUN instructions (max 30)"
  grep -qE '^FROM[[:space:]]+[^[:space:]]+:[^[:space:]]+' Dockerfile \
    || fail "FROM must use pinned tag"
  grep 'apt-get install' Dockerfile | grep -v -- '--no-install-recommends' >/dev/null \
    && fail "apt-get install missing --no-install-recommends" \
    || pass "apt-get uses --no-install-recommends"
  grep -q 'COPY[[:space:]]\+\.[[:space:]]\+\.' Dockerfile \
    || fail "Dockerfile must use COPY . ."
fi

if [[ -f .dockerignore ]] && grep -qE '^\.git/?$' .dockerignore; then
  fail ".dockerignore excludes .git/"
else
  pass ".git included in Docker context"
fi

count=$(python3 -m pytest tests/ --collect-only -q 2>/dev/null | tail -1 | grep -oE '[0-9]+' | head -1 || echo 0)
[[ "${count:-0}" -ge 200 ]] || fail "only ${count:-0} tests collected (need 200+)"
pass "${count} tests collected"

git rev-parse --git-dir >/dev/null 2>&1 || fail "not a git repository"
pass "git repository present"

for path in tests/conftest.py requirements-core.txt Dockerfile; do
  [[ -e "$path" ]] || fail "missing $path"
done
pass "required paths present"

if [[ "$FAIL" -ne 0 ]]; then
  echo "ci-preflight: FAILED" >&2
  exit 1
fi
echo "ci-preflight: ALL CHECKS PASSED"
