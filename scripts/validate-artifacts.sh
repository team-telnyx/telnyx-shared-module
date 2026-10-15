#!/usr/bin/env bash
set -euo pipefail

asset_dir="${1:?usage: validate-artifacts.sh <asset-directory>}"
manifest="$asset_dir/artifacts.json"
test -f "$manifest"

python3 - "$asset_dir" <<'PY'
import hashlib
import json
import pathlib
import zipfile
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / "artifacts.json").read_text())
required = {"version", "source_commit", "swiftpm_checksum", "artifacts"}
missing = required - manifest.keys()
if missing:
    raise SystemExit(f"manifest missing keys: {sorted(missing)}")
if not manifest["artifacts"]:
    raise SystemExit("manifest has no artifacts")
for item in manifest["artifacts"]:
    path = root / item["name"]
    if not path.is_file():
        raise SystemExit(f"missing artifact: {path.name}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != item["sha256"]:
        raise SystemExit(f"SHA-256 mismatch: {path.name}")
    if path.name.endswith(".xcframework.zip"):
        if manifest["swiftpm_checksum"] != digest:
            raise SystemExit(f"SwiftPM checksum mismatch: {path.name}")
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if any(name.startswith("__MACOSX/") for name in names):
                raise SystemExit(f"unexpected macOS metadata: {path.name}")
            required_slices = ("ios-arm64/", "ios-arm64_x86_64-simulator/")
            for required_slice in required_slices:
                if not any(required_slice in name for name in names):
                    raise SystemExit(f"missing {required_slice}: {path.name}")
print(f"validated {len(manifest['artifacts'])} artifacts for {manifest['version']}")
PY
