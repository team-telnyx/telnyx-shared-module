import copy
import hashlib
import importlib.util
import io
import json
import unittest
import zipfile
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

    def test_complete_bundle_preserves_metadata(self):
        files = module.validate_bundle(*self.bundle())
        self.assertEqual(json.loads(files["publication.json"]), self.metadata)

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
