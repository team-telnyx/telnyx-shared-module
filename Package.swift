// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxSharedModule",
    platforms: [.iOS(.v12)],
    products: [.library(name: "TelnyxSharedModule", targets: ["TelnyxSharedModule"])],
    targets: [.binaryTarget(name: "TelnyxSharedModule", url: "https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.2/TelnyxSharedModule-0.2.2.xcframework.zip", checksum: "294432c8a04b2831df0d9afc17d7f8b5a1d4e49a6f5637916cd04770700bab5f")]
)
