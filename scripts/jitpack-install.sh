#!/usr/bin/env bash
set -euo pipefail

# JitPack's base Python may have neither pip nor venv/ensurepip installed.
# Keep dependencies isolated; do not rely on a system pip or mutate its packages.
venv_dir="${TMPDIR:-/tmp}/telnyx-shared-jitpack-venv"
if ! python3 -m venv "$venv_dir"; then
  sudo apt-get update
  sudo apt-get install --yes python3-venv
  python3 -m venv "$venv_dir"
fi
"$venv_dir/bin/python" -m pip install -r scripts/requirements.txt
"$venv_dir/bin/python" scripts/prepare-android.py
./gradlew publishToMavenLocal -Pversion="${VERSION:?JitPack must supply VERSION}"
