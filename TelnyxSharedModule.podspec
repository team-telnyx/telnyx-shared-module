Pod::Spec.new do |s|
  s.name = 'TelnyxSharedModule'
  s.version = '0.2.3'
  s.summary = 'Shared capabilities for Telnyx mobile SDKs.'
  s.homepage = 'https://github.com/team-telnyx/telnyx-shared-module'
  s.author = { 'Telnyx LLC' => 'cocoapods+official@telnyx.com' }
  s.license = { :type => 'Proprietary', :text => 'Copyright Telnyx LLC. All rights reserved.' }
  s.source = { :http => 'https://github.com/team-telnyx/telnyx-shared-module/releases/download/0.2.3/TelnyxSharedModule-0.2.3.xcframework.zip', :sha256 => '2f77f3f4f343baa3116ee43793a28bb0cf13340ea016eaf4e850fa87cd0565ba' }
  s.ios.deployment_target = '12.0'
  s.vendored_frameworks = 'TelnyxSharedModule.xcframework'
  s.static_framework = true
  s.libraries = 'c++'
end
