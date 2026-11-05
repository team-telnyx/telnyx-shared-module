// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "TelnyxSharedModule",
    platforms: [.iOS(.v12)],
    products: [.library(name: "TelnyxSharedModule", targets: ["TelnyxSharedModule"])],
    targets: [.binaryTarget(name: "TelnyxSharedModule", url: "https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.3/TelnyxSharedModule-0.2.3.xcframework.zip", checksum: "2f77f3f4f343baa3116ee43793a28bb0cf13340ea016eaf4e850fa87cd0565ba")]
)
