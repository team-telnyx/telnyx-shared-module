import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import unittest
import zipfile
from unittest.mock import patch, Mock
from pathlib import Path

spec = importlib.util.spec_from_file_location("prepare_android", Path(__file__).resolve().parents[1] / "scripts/prepare-android.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def zip_bytes(files):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return data.getvalue()


class AndroidPublicationTest(unittest.TestCase):
    def setUp(self):
        self.aar = zip_bytes({"classes.jar": zip_bytes({})})
        self.metadata = {"schema_version": 1, "version": "1.2.3", "source_commit": "a" * 40,
                         "modules": [{"name": name, "file": f"{name}.aar", "sha256": hashlib.sha256(self.aar).hexdigest(),
                                      "dependencies": []} for name in sorted(module.MODULES)]}
        self.metadata["modules"][0]["dependencies"] = [{"group": "org.jetbrains.kotlin", "artifact": "kotlin-stdlib", "version": "1.9.23", "scope": "runtime",
                                                      "exclusions": [{"group": "org.jetbrains.kotlin", "artifact": "kotlin-stdlib-common"}]}]

    def bundle(self, metadata=None, extra=None):
        files = {f"{name}.aar": self.aar for name in module.MODULES}
        files["publication.json"] = json.dumps(metadata or self.metadata).encode()
        files.update(extra or {})
        data = zip_bytes(files)
        release = {"version": "1.2.3", "source_commit": "a" * 40, "sha256": hashlib.sha256(data).hexdigest()}
        return data, release

    def test_release_download_uses_fixed_https_and_checks_status(self):
        data, release = self.bundle()
        response = Mock(content=data)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "android-release.json").write_text(json.dumps(release))
            with patch.object(module, "ROOT", root), patch("sys.argv", ["prepare-android.py"]), patch.object(module.requests, "get", return_value=response) as get:
                module.main()
            get.assert_called_once_with("https://github.com/team-telnyx/telnyx-webrtc-kmp-binaries/releases/download/1.2.3/telnyx-observability-android-1.2.3.zip", timeout=120)
            response.raise_for_status.assert_called_once_with()
            self.assertTrue((root / "incoming/android/publication.json").is_file())

    def test_version_cannot_inject_download_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "android-release.json").write_text(json.dumps({"version": "file:///etc/passwd"}))
            with patch.object(module, "ROOT", root), patch("sys.argv", ["prepare-android.py"]), patch.object(module.requests, "get") as get:
                with self.assertRaisesRegex(ValueError, "Invalid binary release version"):
                    module.main()
                get.assert_not_called()

    def test_failed_download_does_not_write_artifacts(self):
        _, release = self.bundle()
        response = Mock()
        response.raise_for_status.side_effect = module.requests.HTTPError("404")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "android-release.json").write_text(json.dumps(release))
            with patch.object(module, "ROOT", root), patch("sys.argv", ["prepare-android.py"]), patch.object(module.requests, "get", return_value=response):
                with self.assertRaises(module.requests.HTTPError):
                    module.main()
            self.assertFalse((root / "incoming").exists())

    def test_complete_bundle_preserves_metadata(self):
        files = module.validate_bundle(*self.bundle())
        self.assertEqual(json.loads(files["publication.json"]), self.metadata)

    @unittest.skipUnless(os.environ.get("TEST_GRADLE_PUBLICATION") == "1", "enable for Java/Gradle integration")
    def test_gradle_publishes_complete_poms(self):
        metadata = copy.deepcopy(self.metadata)
        api = next(m for m in metadata["modules"] if m["name"] == "observability-api")
        api["dependencies"].append({"module": "observability-core", "scope": "compile"})
        files = module.validate_bundle(*self.bundle(metadata))
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            for name in ("build.gradle", "settings.gradle"):
                shutil.copy2(root / name, project / name)
            incoming = project / "incoming/android"
            incoming.mkdir(parents=True)
            for name, data in files.items():
                (incoming / name).write_bytes(data)
            repository = project / "maven"
            result = subprocess.run([str(root / "gradlew"), "-p", str(project), "publishToMavenLocal",
                                     "-Pversion=fixture-publication", f"-Dmaven.repo.local={repository}", "--console=plain"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            group = "com.github.team-telnyx.telnyx-webrtc-kmp-binaries"
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            for name in module.MODULES:
                path = repository / group.replace(".", "/") / name / "fixture-publication" / f"{name}-fixture-publication.pom"
                pom = ET.parse(path).getroot()
                self.assertEqual(pom.findtext("m:packaging", namespaces=ns), "aar")
                if name == "observability-api":
                    deps = pom.findall("m:dependencies/m:dependency", ns)
                    core = next(d for d in deps if d.findtext("m:artifactId", namespaces=ns) == "observability-core")
                    self.assertEqual(core.findtext("m:groupId", namespaces=ns), group)
                    self.assertEqual(core.findtext("m:version", namespaces=ns), "fixture-publication")
                    kotlin = next(d for d in deps if d.findtext("m:artifactId", namespaces=ns) == "kotlin-stdlib")
                    self.assertEqual(kotlin.findtext("m:scope", namespaces=ns), "runtime")
                    self.assertEqual(len(kotlin.findall("m:exclusions/m:exclusion", ns)), 1)

    def test_tampered_bundle(self):
        data, release = self.bundle()
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            module.validate_bundle(data + b"tampered", release)

    def test_source_mismatch(self):
        data, release = self.bundle()
        release["source_commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "provenance"):
            module.validate_bundle(data, release)

    def test_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "entries"):
            module.validate_bundle(*self.bundle(extra={"../escape": b"bad"}))

    def test_missing_module(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["modules"].pop()
        with self.assertRaisesRegex(ValueError, "four Android"):
            module.validate_bundle(*self.bundle(metadata))

    def test_inexact_dependency(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["modules"][0]["dependencies"][0]["version"] = "1.+"
        with self.assertRaisesRegex(ValueError, "exact external"):
            module.validate_bundle(*self.bundle(metadata))

    def test_inner_aar_tampering(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["modules"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "AAR SHA-256"):
            module.validate_bundle(*self.bundle(metadata))


if __name__ == "__main__":
    unittest.main()
