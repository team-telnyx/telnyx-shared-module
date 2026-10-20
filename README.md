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
the run provenance, downloads with a short-lived GitHub App installation token, verifies artifacts,
and parses the generated Swift package. It does not upload candidate binaries or
create commits, tags, or releases. Configure the App with repository **Actions: read-only**, disable webhooks, and
install it only on `team-telnyx/telnyx-webrtc-kmp-shared-module`.

In **this binaries repository** (not the source repository), configure repository
Actions secrets:
- `KMP_SOURCE_APP_ID`: the App ID (a repository variable of the same name is also supported).
- `KMP_SOURCE_APP_PRIVATE_KEY`: the complete PEM private key generated in the App settings.

Repository secrets are required for the private key because the validation job
runs without a deployment environment. No App installation on this public repo
is needed. The pinned official `actions/create-github-app-token` action requests
only Actions read access to the named source repository, and revokes the generated
token after each job. No PAT or stored installation token is used.

Publication is a separate job, enabled only with `dry_run=false`, and must only
be dispatched after explicit approval for that specific release. Before doing so,
configure the `binary-release` environment with required reviewers. The workflow
refuses publication without reviewers or when the version already exists.
