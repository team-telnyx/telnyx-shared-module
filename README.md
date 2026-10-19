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

## Candidate validation (no publication)

Run `publish-approved-release` with `dry_run=true` (the default), the successful
private source run ID, its exact head SHA, and version. The validation job checks
the run provenance, downloads with `KMP_SOURCE_REPO_TOKEN`, verifies artifacts,
and parses the generated Swift package. It does not upload candidate binaries or
create commits, tags, or releases. Configure that secret using a narrowly scoped
credential with Actions read access to the internal source repository; do not
copy a broad personal CLI token into Actions.

Publication is a separate job, enabled only with `dry_run=false`, and must only
be dispatched after explicit approval for that specific release. Before doing so,
configure the `binary-release` environment with required reviewers. The workflow
refuses publication without reviewers or when the version already exists.
