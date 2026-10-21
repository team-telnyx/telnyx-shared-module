#!/usr/bin/env python3
"""Render matching SwiftPM and CocoaPods metadata from a verified candidate."""
import argparse
import json
from pathlib import Path
import re


def render(candidate, output):
    manifest = json.loads((candidate / 'artifacts.json').read_text())
    version = manifest['version']
    checksum = manifest['swiftpm_checksum']
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('Invalid version')
    if not re.fullmatch(r'[0-9a-f]{64}', checksum):
        raise ValueError('Invalid checksum')
    asset = f'TelnyxSharedModule-{version}.xcframework.zip'
    if not any(a['name'] == asset and a['sha256'] == checksum for a in manifest['artifacts']):
        raise ValueError('Apple artifact does not match SwiftPM checksum')
    url = f'https://github.com/team-telnyx/telnyx-shared-module/releases/download/{version}/{asset}'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'Package.swift').write_text(f'''// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxSharedModule",
    platforms: [.iOS(.v13)],
    products: [.library(name: "TelnyxSharedModule", targets: ["TelnyxSharedModule"])],
    targets: [.binaryTarget(name: "TelnyxSharedModule", url: "{url}", checksum: "{checksum}")]
)
''')
    (output / 'TelnyxSharedModule.podspec').write_text(f'''Pod::Spec.new do |s|
  s.name = 'TelnyxSharedModule'
  s.version = '{version}'
  s.summary = 'Shared capabilities for Telnyx mobile SDKs.'
  s.homepage = 'https://github.com/team-telnyx/telnyx-shared-module'
  s.author = {{ 'Telnyx LLC' => 'cocoapods+official@telnyx.com' }}
  s.license = {{ :type => 'Proprietary', :text => 'Copyright Telnyx LLC. All rights reserved.' }}
  s.source = {{ :http => '{url}', :sha256 => '{checksum}' }}
  s.ios.deployment_target = '13.0'
  s.vendored_frameworks = 'TelnyxSharedModule.xcframework'
  s.static_framework = true
  s.libraries = 'c++'
end
''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--output', type=Path, default=Path('.'))
    args = parser.parse_args()
    render(args.candidate, args.output)
