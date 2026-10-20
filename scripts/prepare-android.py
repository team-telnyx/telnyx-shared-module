#!/usr/bin/env python3
"""Verify public release inputs and materialize a source-free Android publication."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import requests
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULES = {"shared-foundation", "observability-contract", "observability-core", "observability-api"}
COORDINATE = re.compile(r"[A-Za-z0-9_.-]+")


def validate_bundle(data, release):
    if hashlib.sha256(data).hexdigest() != release["sha256"]:
        raise ValueError("Android bundle SHA-256 mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        expected = {"publication.json"} | {f"{name}.aar" for name in MODULES}
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != expected:
            raise ValueError("Unexpected Android bundle entries")
        metadata = json.loads(archive.read("publication.json"))
        if metadata["schema_version"] != 1 or metadata["version"] != release["version"] or metadata["source_commit"] != release["source_commit"]:
            raise ValueError("Android bundle provenance mismatch")
        if len(metadata["modules"]) != 4 or {m["name"] for m in metadata["modules"]} != MODULES:
            raise ValueError("Expected all four Android modules")
        for module in metadata["modules"]:
            if module["file"] != f"{module['name']}.aar":
                raise ValueError("Invalid AAR filename")
            aar = archive.read(module["file"])
            if hashlib.sha256(aar).hexdigest() != module["sha256"]:
                raise ValueError("AAR SHA-256 mismatch")
            with zipfile.ZipFile(io.BytesIO(aar)) as contents:
                if "classes.jar" not in contents.namelist() or contents.testzip():
                    raise ValueError("Invalid AAR")
            for dep in module["dependencies"]:
                if dep["scope"] not in ("compile", "runtime"):
                    raise ValueError("Invalid dependency scope")
                if "module" in dep:
                    if dep["module"] not in MODULES or dep["module"] == module["name"]:
                        raise ValueError("Invalid internal dependency")
                elif not all(COORDINATE.fullmatch(dep[k]) for k in ("group", "artifact", "version")):
                    raise ValueError("Expected exact external dependency coordinates")
                for rule in dep.get("exclusions", []):
                    if not all(rule[k] == "*" or COORDINATE.fullmatch(rule[k]) for k in ("group", "artifact")):
                        raise ValueError("Invalid dependency exclusion")
        return {name: archive.read(name) for name in expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, help="Local validation only: read private CI candidate instead of a public release")
    args = parser.parse_args()
    if args.candidate_dir:
        manifest = json.loads((args.candidate_dir / "artifacts.json").read_text())
        name = f"telnyx-observability-android-{manifest['version']}.zip"
        asset = next(a for a in manifest["artifacts"] if a["name"] == name)
        release = {"version": manifest["version"], "source_commit": manifest["source_commit"], "sha256": asset["sha256"]}
        data = (args.candidate_dir / name).read_bytes()
    else:
        config = ROOT / "android-release.json"
        if not config.exists():
            raise SystemExit("No Android publication release configured. Existing 0.1.0 is API-only; a new approved candidate/release is required.")
        release = json.loads(config.read_text())
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", release["version"]):
            raise ValueError("Invalid binary release version")
        url = f"https://github.com/team-telnyx/telnyx-webrtc-kmp-binaries/releases/download/{release['version']}/telnyx-observability-android-{release['version']}.zip"
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        data = response.content
    files = validate_bundle(data, release)
    target = ROOT / "incoming/android"
    target.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (target / name).write_bytes(data)
    print(f"Verified four Android modules from {release['source_commit']}")


if __name__ == "__main__":
    main()
