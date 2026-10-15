# Telnyx WebRTC KMP Binaries

Public, source-free distribution metadata for binary artifacts built from the
private Telnyx WebRTC KMP shared-module repository.

## Apple

Swift Package Manager consumers use this repository. Each immutable GitHub
release contains a versioned `TelnyxObservability.xcframework.zip`; the tagged
`Package.swift` references that asset and pins its SwiftPM checksum.

No release exists yet. Publication is manual and approval-gated.

## Android

Android artifacts may also be attached to releases for inspection or manual
integration. Normal Android SDK consumption remains transitive through the
published Telnyx SDK dependency, so customers should not download AARs by hand.

## Integrity and provenance

Each release must include `artifacts.json`, containing the source commit,
artifact names, SHA-256 hashes, and the SwiftPM checksum. Published versions
are immutable and must never be overwritten.
