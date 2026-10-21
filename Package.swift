// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxSharedModule",
    platforms: [.iOS(.v12)],
    products: [
        .library(
            name: "TelnyxSharedModule",
            targets: ["TelnyxObservability"]
        )
    ],
    // 0.1.0 is immutable: its existing binary still exports TelnyxObservability.
    // Future approved releases use the TelnyxSharedModule framework.
    targets: [
        .binaryTarget(
            name: "TelnyxObservability",
            url: "https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.1.0/TelnyxObservability-0.1.0.xcframework.zip",
            checksum: "c51c97c3613facd61bad5dd36f4dad36c6498d092d5e81b32e5cc387adc791ec"
        )
    ]
)
