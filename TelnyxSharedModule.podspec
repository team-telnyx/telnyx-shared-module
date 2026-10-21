Pod::Spec.new do |s|
  s.name = 'TelnyxSharedModule'
  s.version = '0.2.2'
  s.summary = 'Shared capabilities for Telnyx mobile SDKs.'
  s.homepage = 'https://github.com/team-telnyx/telnyx-shared-module'
  s.author = { 'Telnyx LLC' => 'cocoapods+official@telnyx.com' }
  s.license = { :type => 'Proprietary', :text => 'Copyright Telnyx LLC. All rights reserved.' }
  s.source = { :http => 'https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.2/TelnyxSharedModule-0.2.2.xcframework.zip', :sha256 => '294432c8a04b2831df0d9afc17d7f8b5a1d4e49a6f5637916cd04770700bab5f' }
  s.ios.deployment_target = '12.0'
  s.vendored_frameworks = 'TelnyxSharedModule.xcframework'
  s.static_framework = true
  s.libraries = 'c++'
end
