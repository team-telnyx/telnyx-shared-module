Pod::Spec.new do |s|
  s.name = 'TelnyxSharedModule'
  s.version = '0.2.0'
  s.summary = 'Shared capabilities for Telnyx mobile SDKs.'
  s.homepage = 'https://github.com/team-telnyx/telnyx-shared-module'
  s.author = { 'Telnyx LLC' => 'cocoapods+official@telnyx.com' }
  s.license = { :type => 'Proprietary', :text => 'Copyright Telnyx LLC. All rights reserved.' }
  s.source = { :http => 'https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.0/TelnyxSharedModule-0.2.0.xcframework.zip', :sha256 => '35e261f158bc5a22b617faec1aa26d5c82b5ceebc129895017a94ace4ad6a303' }
  s.ios.deployment_target = '12.0'
  s.vendored_frameworks = 'TelnyxSharedModule.xcframework'
  s.static_framework = true
  s.libraries = 'c++'
end
