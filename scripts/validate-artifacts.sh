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
import re

root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / "artifacts.json").read_text())
required = {"version", "source_commit", "swiftpm_checksum", "artifacts"}
missing = required - manifest.keys()
if missing:
    raise SystemExit(f"manifest missing keys: {sorted(missing)}")
version = manifest["version"]
if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
    raise SystemExit("invalid version")
if not re.fullmatch(r"[0-9a-f]{40}", manifest["source_commit"]):
    raise SystemExit("invalid source commit")
expected = {f"TelnyxObservability-{version}.xcframework.zip", f"telnyx-observability-{version}.aar"}
if len(manifest["artifacts"]) != 2 or {item["name"] for item in manifest["artifacts"]} != expected:
    raise SystemExit("expected exactly the versioned XCFramework ZIP and Android AAR")
if {path.name for path in root.iterdir()} != expected | {"artifacts.json"}:
    raise SystemExit("unexpected files in artifact directory")
for item in manifest["artifacts"]:
    path = root / item["name"]
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"missing artifact: {path.name}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != item["sha256"]:
        raise SystemExit(f"SHA-256 mismatch: {path.name}")
    if path.name.endswith(".xcframework.zip"):
        if manifest["swiftpm_checksum"] != digest:
            raise SystemExit(f"SwiftPM checksum mismatch: {path.name}")
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if archive.testzip() is not None:
                raise SystemExit(f"corrupt ZIP: {path.name}")
            if any(pathlib.PurePosixPath(name).is_absolute() or ".." in pathlib.PurePosixPath(name).parts for name in names):
                raise SystemExit(f"unsafe ZIP path: {path.name}")
            if any("__MACOSX" in pathlib.PurePosixPath(name).parts for name in names):
                raise SystemExit(f"unexpected macOS metadata: {path.name}")
            required_slices = ("ios-arm64/", "ios-arm64_x86_64-simulator/")
            for required_slice in required_slices:
                if not any(required_slice in name for name in names):
                    raise SystemExit(f"missing {required_slice}: {path.name}")
print(f"validated {len(manifest['artifacts'])} artifacts for {manifest['version']}")
PY
