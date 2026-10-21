import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('apple', Path(__file__).resolve().parents[1] / 'scripts/render-apple-metadata.py')
apple = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apple)


class AppleMetadataTest(unittest.TestCase):
    def test_matching_distribution_identity_and_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checksum = 'a' * 64
            manifest = {'version': '0.2.0', 'swiftpm_checksum': checksum,
                        'artifacts': [{'name': 'TelnyxSharedModule-0.2.0.xcframework.zip', 'sha256': checksum}]}
            (root / 'artifacts.json').write_text(json.dumps(manifest))
            apple.render(root, root)
            for name in ['Package.swift', 'TelnyxSharedModule.podspec']:
                text = (root / name).read_text()
                self.assertIn('https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.0/TelnyxSharedModule-0.2.0.xcframework.zip', text)
                self.assertIn(checksum, text)
                self.assertNotIn('KMP', text)
                self.assertNotIn('TelnyxObservability', text)
            manifest['artifacts'][0]['sha256'] = 'b' * 64
            (root / 'artifacts.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'checksum'):
                apple.render(root, root)

    def test_version_cannot_inject_swift_or_ruby(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'artifacts.json').write_text(json.dumps({'version': "0.2.0'; system('bad')", 'swiftpm_checksum': 'a' * 64}))
            with self.assertRaisesRegex(ValueError, 'version'):
                apple.render(root, root)
