// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxWebRTCKMPBinaries",
    platforms: [.iOS(.v12)],
    products: [
        .library(
            name: "TelnyxObservability",
            targets: ["TelnyxObservability"]
        )
    ],
    targets: [
        .binaryTarget(
            name: "TelnyxObservability",
            url: "https://github.com/team-telnyx/telnyx-webrtc-kmp-binaries/releases/download/0.1.0/TelnyxObservability-0.1.0.xcframework.zip",
            checksum: "c51c97c3613facd61bad5dd36f4dad36c6498d092d5e81b32e5cc387adc791ec"
        )
    ]
)
