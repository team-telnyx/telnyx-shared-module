package com.telnyx.kmp.consumer

import com.telnyx.webrtc.mobile.shared.observability.api.ObservabilityFactory
import com.telnyx.webrtc.mobile.shared.observability.core.ObservabilityModule

// Compilation requires both the API and its transitive core module.
fun createObservability(): ObservabilityModule = ObservabilityFactory.create()
