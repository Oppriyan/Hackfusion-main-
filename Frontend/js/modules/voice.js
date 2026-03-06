import { ChatAPI, AuthAPI } from "../api.js";

export function initVoice() {
  // ============================================================
  // VAPI VOICE INTEGRATION
  // ============================================================

  /**
   * Initialize VAPI voice call
   * Requires VAPI SDK to be loaded
   */
  window.initVoiceCall = async function () {
    // Check if VAPI SDK is available
    if (!window.VAPI) {
      console.warn("VAPI SDK not loaded. Loading now...");
      try {
        await loadVAPISDK();
      } catch (error) {
        console.error("Failed to load VAPI:", error);
        showToast("Failed to load voice module", "error");
        return;
      }
    }

    // Check microphone permission first
    const hasMicAccess = await checkMicrophonePermission();
    if (!hasMicAccess) {
      return;
    }

    console.log("Initializing VAPI voice call...");

    // Get current user
    const user = AuthAPI.getCurrentUser();
    const customerId = user?.id || "PAT999";

    try {
      // Initialize VAPI with config
      const config = {
        apiKey: window.VAPI_PUBLIC_KEY || "",
        agentId: window.VAPI_AGENT_ID || "",
        customData: {
          customer_id: customerId,
          timestamp: new Date().toISOString(),
        },
        webhookUrl: window.VAPI_WEBHOOK_URL || "http://localhost:5000/chat/voice-webhook",
      };

      // Important: Make sure VAPI SDK is properly configured
      if (window.VAPI && typeof window.VAPI.start === "function") {
        window.VAPI.start(config);
        console.log("✅ Voice call started");
        showToast("Speak now - listening for your voice", "success");
        
        // Emit event
        emitVoiceEvent("call_started", { customer_id: customerId });
      } else {
        console.error("VAPI.start not available");
        showToast("Voice module not ready", "error");
      }
    } catch (error) {
      console.error("Failed to start voice call:", error);
      showToast("Failed to start voice call", "error");
    }
  };

  /**
   * Stop ongoing voice call
   */
  window.stopVoiceCall = function () {
    try {
      if (window.VAPI && typeof window.VAPI.stop === "function") {
        window.VAPI.stop();
        console.log("✅ Voice call stopped");
        showToast("Voice call ended");
        
        // Emit event
        emitVoiceEvent("call_stopped", {});
      } else {
        console.warn("VAPI.stop not available");
      }
    } catch (error) {
      console.error("Error stopping voice call:", error);
    }
  };

  /**
   * Load VAPI SDK dynamically
   */
  window.loadVAPISDK = function () {
    return new Promise((resolve, reject) => {
      if (window.VAPI) {
        console.log("VAPI SDK already loaded");
        resolve();
        return;
      }

      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/vapi-js@latest";
      script.async = true;

      script.onload = () => {
        console.log("✅ VAPI SDK loaded successfully");
        
        // Initialize VAPI client
        if (window.Vapi) {
          window.VAPI = new window.Vapi({
            apiKey: window.VAPI_PUBLIC_KEY || "",
          });
          console.log("✅ VAPI client initialized");
        }
        
        resolve();
      };

      script.onerror = () => {
        console.error("❌ Failed to load VAPI SDK");
        reject(new Error("VAPI SDK load failed"));
      };

      document.head.appendChild(script);
    });
  };

  // Create alias
  const loadVAPISDK = window.loadVAPISDK;

  /**
   * Check microphone permission
   */
  window.checkMicrophonePermission = async function () {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      stream.getTracks().forEach((track) => track.stop());
      console.log("✅ Microphone permission granted");
      return true;
    } catch (error) {
      console.error("❌ Microphone permission denied:", error);
      showToast("Please enable microphone to use voice chat", "error");
      return false;
    }
  };

  /**
   * Handle voice message (called from agent response)
   */
  window.handleVoiceResponse = function (response) {
    const message = response.message || response.data?.reply;

    if (!message) {
      console.warn("No message in voice response");
      return;
    }

    console.log("📝 Voice response:", message);

    // Display response in chat
    const chatBox = document.getElementById("chatBox");
    if (chatBox) {
      const msgEl = document.createElement("div");
      msgEl.className = "chat-message bot";
      msgEl.textContent = message;
      chatBox.appendChild(msgEl);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    // If using VAPI for TTS, it will handle playback automatically
    // Otherwise, use Web Audio API
    if (window.VAPI_USE_TTS !== false) {
      // VAPI handles TTS - response already sent to VAPI
      console.log("🎤 VAPI handling text-to-speech");
    } else {
      // Fallback: Use browser TTS
      console.log("🔊 Using browser speech synthesis");
      speakMessage(message);
    }

    // Emit event
    emitVoiceEvent("message_received", { message });
  };

  /**
   * Fallback: Speak message using Web Audio API (browser TTS)
   */
  window.speakMessage = function (message) {
    if (!("speechSynthesis" in window)) {
      console.warn("Speech synthesis not supported in this browser");
      return;
    }

    try {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(message);
      utterance.lang = "en-US";
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;

      utterance.onstart = () => {
        console.log("🔊 Speaking...");
        emitVoiceEvent("speaking_start", {});
      };

      utterance.onend = () => {
        console.log("✅ Speaking finished");
        emitVoiceEvent("speaking_end", {});
      };

      utterance.onerror = (error) => {
        console.error("Speech synthesis error:", error);
        emitVoiceEvent("speaking_error", { error: error.error });
      };

      window.speechSynthesis.speak(utterance);
    } catch (error) {
      console.error("Error in speakMessage:", error);
    }
  };

  /**
   * Configure VAPI before initialization
   * Call this during app initialization
   */
  window.configureVAPI = function (publicKey, agentId, webhookUrl) {
    window.VAPI_PUBLIC_KEY = publicKey;
    window.VAPI_AGENT_ID = agentId;
    window.VAPI_WEBHOOK_URL = webhookUrl || "http://localhost:5000/chat/voice-webhook";
    window.VAPI_USE_TTS = true; // Use VAPI for TTS by default

    console.log("✅ VAPI configured");
    console.log("  - Agent ID:", agentId);
    console.log("  - Webhook URL:", webhookUrl);
  };

  /**
   * Get voice call status
   */
  window.getVoiceCallStatus = function () {
    if (window.VAPI) {
      return {
        isActive: typeof window.VAPI.isActive === "function" ? window.VAPI.isActive() : false,
        status: typeof window.VAPI.getStatus === "function" ? window.VAPI.getStatus() : "unknown",
      };
    }
    return { isActive: false, status: "sdk_not_loaded" };
  };

  /**
   * Emit custom events for voice interactions
   */
  window.emitVoiceEvent = function (eventType, data) {
    const event = new CustomEvent("voiceEvent", {
      detail: { type: eventType, data: data, timestamp: new Date().toISOString() },
    });
    document.dispatchEvent(event);
  };

  /**
   * Listen for voice events
   */
  document.addEventListener("voiceEvent", (e) => {
    const { type, data, timestamp } = e.detail;
    console.log(`[${timestamp}] Voice event - ${type}:`, data);
    
    // Handle specific events
    switch (type) {
      case "call_started":
        console.log("📞 Call started -", data.customer_id);
        break;
      case "call_stopped":
        console.log("📞 Call stopped");
        break;
      case "message_received":
        console.log("💬 Message received");
        break;
      case "speaking_start":
        console.log("🔊 Speaking started");
        break;
      case "speaking_end":
        console.log("🔊 Speaking ended");
        break;
      default:
        console.log("Voice event:", type);
    }
  });

  /**
   * Get voice permissions and status
   */
  window.getVoicePermissions = async function () {
    try {
      const permissions = await navigator.permissions.query({ name: "microphone" });
      return {
        mic_status: permissions.state, // "granted", "denied", "prompt"
        api_ready: !!window.VAPI,
        sdk_loaded: !!window.Vapi,
      };
    } catch (error) {
      console.error("Error getting permissions:", error);
      return {
        mic_status: "unknown",
        api_ready: !!window.VAPI,
        sdk_loaded: !!window.Vapi,
      };
    }
  };

  console.log("✅ Voice module initialized");
}

// Export for module usage
export { loadVAPISDK };

