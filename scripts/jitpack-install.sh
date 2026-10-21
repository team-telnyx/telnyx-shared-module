#!/usr/bin/env bash
set -euo pipefail

# Use only the Python standard library: JitPack may lack pip, ensurepip and sudo.
python3 -S scripts/prepare-android.py
./gradlew publishToMavenLocal -Pversion="${VERSION:?JitPack must supply VERSION}"
