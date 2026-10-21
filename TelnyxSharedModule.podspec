Pod::Spec.new do |s|
  s.name = 'TelnyxSharedModule'
  s.version = '0.2.1'
  s.summary = 'Shared capabilities for Telnyx mobile SDKs.'
  s.homepage = 'https://github.com/team-telnyx/telnyx-shared-module'
  s.author = { 'Telnyx LLC' => 'cocoapods+official@telnyx.com' }
  s.license = { :type => 'Proprietary', :text => 'Copyright Telnyx LLC. All rights reserved.' }
  s.source = { :http => 'https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.1/TelnyxSharedModule-0.2.1.xcframework.zip', :sha256 => '6041a61cc564f23a5a2a1b29d7d84710086bdf00a6184e9bad1f818186b78658' }
  s.ios.deployment_target = '12.0'
  s.vendored_frameworks = 'TelnyxSharedModule.xcframework'
  s.static_framework = true
  s.libraries = 'c++'
end
