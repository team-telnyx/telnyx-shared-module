# Telnyx WebRTC KMP Binaries

Public, source-free distribution metadata for binary artifacts built from the
private Telnyx WebRTC KMP shared-module repository.

## Apple

Swift Package Manager consumers use this repository. Each immutable GitHub
release contains a versioned `TelnyxObservability.xcframework.zip`; the tagged
`Package.swift` references that asset and pins its SwiftPM checksum.

Publication is manual and approval-gated. Consumers must select an exact release version.
The release manifest is committed to its immutable tag; the workflow never pushes
to PR-protected `main`.

## Android

JitPack runs `jitpack.yml`: download the immutable Android bundle pinned in
`android-release.json`, verify its checksum and per-AAR hashes/provenance, and
run Gradle `publishToMavenLocal`. No private source or credentials reach JitPack.
This is Android AAR/POM publication, not a common-source Kotlin Multiplatform
publication. Four modules are published with exact internal version pins:
`shared-foundation`, `observability-contract`, `observability-core`, and
`observability-api`. External dependencies, runtime scopes and exclusions come
from the private build's generated Android release POMs.

After a complete release is approved and published, the native Android SDK adds:

```kotlin
repositories { maven { url = uri("https://jitpack.io") } }
dependencies {
    implementation("com.github.team-telnyx.telnyx-webrtc-kmp-binaries:observability-api:<approved-version>")
}
```

Customers continue installing the native SDK; KMP modules resolve transitively.
The existing `0.1.0` release does **not** contain the complete Android bundle or
JitPack setup and cannot be used for this path. Do not move its tag or replace
its assets. A new candidate and separately approved release are required.
`android-release.json` is generated and committed with `Package.swift` to the
new immutable release tag, not `main`.

### Validation without publishing a release

Build the four Android release AARs/POMs in the private source repository and run
`scripts/export-android-publication.py <candidate-version> <bundle-path> <full-source-commit>`.
Use the candidate's `artifacts.json` and bundle locally:

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/prepare-android.py --candidate-dir /path/to/candidate
./gradlew publishToMavenLocal -Pversion=local-validation -Dmaven.repo.local=/tmp/kmp-maven
KMP_MAVEN_REPO=/tmp/kmp-maven ./gradlew -p verification/android-consumer \
  assembleRelease dependencies --configuration releaseRuntimeClasspath \
  -PsmokeVersion=local-validation
```

The consumer only declares the API dependency and compiles a factory call whose
return type is in core. Use an empty Maven directory for a clean check.
After publication, omit `KMP_MAVEN_REPO` and use the approved version in
`smokeVersion` to test actual JitPack resolution; requesting that version can
trigger JitPack's build/publication. This hosted check is a release step and
requires the corresponding approval. The native SDK should pin that exact version.

## CocoaPods compatibility

The native iOS SDK has `TelnyxRTC.podspec` and a manually dispatched
`release-04-deploy-cocoapods` workflow which lints it and runs `pod trunk push`
using `COCOAPODS_TRUNK_TOKEN`. It distributes Swift sources, whereas this repo
would distribute the precompiled framework.

For KMP, a `TelnyxObservability.podspec` should specify the matching version,
iOS deployment target, an HTTP `source` pointing to the immutable XCFramework
ZIP with `:sha256`, and
`vendored_frameworks = 'TelnyxObservability.xcframework'`. Validate with
`pod spec lint` and a clean iOS consumer, then have `TelnyxRTC.podspec` depend on
that exact pod version. Flutter/RN podspecs can consume the same binary pod.
SPM and CocoaPods users must not link two copies of the static framework.

CocoaPods [announced public trunk becoming read-only on December 2, 2026](https://blog.cocoapods.org/CocoaPods-Specs-Repo/).
Do not make new trunk submissions the only supported path: host binary podspecs
in a public Specs repository, or let direct consumers reference this Git repo's
versioned podspec. Native SDK transitive pod dependencies require the Specs
repository to be configured by the consumer; a podspec cannot embed a Git URL in
`spec.dependency`. Flutter/RN can instead vendor the framework through their
existing package distribution where appropriate. No pod or release is published
by this implementation.

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

If a run creates a tag but fails before release upload, do not rerun blindly or
move/delete the tag. Verify its manifest and checksum against the original source
candidate, then complete the release on that existing tag after the release
approval. A GitHub release is separate from JitPack/Maven publication.
