// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxSharedModule",
    platforms: [.iOS(.v12)],
    products: [.library(name: "TelnyxSharedModule", targets: ["TelnyxSharedModule"])],
    targets: [.binaryTarget(name: "TelnyxSharedModule", url: "https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.0/TelnyxSharedModule-0.2.0.xcframework.zip", checksum: "35e261f158bc5a22b617faec1aa26d5c82b5ceebc129895017a94ace4ad6a303")]
)
