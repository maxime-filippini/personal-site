#!/usr/bin/env bash

set -euo pipefail

: "${REPO_URL:?Set REPO_URL}"
: "${REPO_BRANCH:=main}"

mkdir -p /data

if [ ! -d /data/content/.git ]; then
  echo "Cloning ${REPO_URL}..."
  git clone --depth=1 --branch "${REPO_BRANCH}" "${REPO_URL}" /data/content
else
  echo "Using existing repo; fetching latest..."
  git -C /data/content fetch --all --prune
fi

# Ensure we’re on a detached HEAD at the latest commit of the branch
LATEST_SHA=$(git -C /data/content rev-parse origin/"${REPO_BRANCH}")
git -C /data/content checkout --detach "${LATEST_SHA}"
echo -n "${LATEST_SHA}" > /data/.VERSION
echo "Active content sha: ${LATEST_SHA}"

# Run the app in production mode
exec uv run fastapi run src/server/main.py --host 0.0.0.0 --port 33000
