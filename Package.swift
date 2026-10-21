// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxSharedModule",
    platforms: [.iOS(.v12)],
    products: [.library(name: "TelnyxSharedModule", targets: ["TelnyxSharedModule"])],
    targets: [.binaryTarget(name: "TelnyxSharedModule", url: "https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.1/TelnyxSharedModule-0.2.1.xcframework.zip", checksum: "6041a61cc564f23a5a2a1b29d7d84710086bdf00a6184e9bad1f818186b78658")]
)
