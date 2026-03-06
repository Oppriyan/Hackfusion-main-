import { ChatAPI, AuthAPI } from "../api.js";

export function initChatbot() {
  const input = document.getElementById("chatInput");
  const chatBox = document.getElementById("chatBox");

  if (!input) return;

  window.sendChatMsg = async function () {
    const message = input.value.trim();

    if (!message) return;

    try {
      // Add user message to chat display
      if (chatBox) {
        const userMsg = document.createElement("div");
        userMsg.className = "chat-message user";
        userMsg.textContent = message;
        chatBox.appendChild(userMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
      }

      input.value = "";

      // Get current user
      const user = AuthAPI.getCurrentUser();
      const customerId = user?.id || "PAT999";

      // Send to API
      const response = await ChatAPI.sendMessage(message, customerId);

      if (response.status === "success" && chatBox) {
        const botMsg = document.createElement("div");
        botMsg.className = "chat-message bot";
        botMsg.textContent =
          response.data?.reply || response.message || "Bot: I understood your message.";
        chatBox.appendChild(botMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
      } else {
        console.error("Chat API error:", response);
        if (chatBox) {
          const errorMsg = document.createElement("div");
          errorMsg.className = "chat-message bot error";
          errorMsg.textContent = "Sorry, I couldn't process that. Please try again.";
          chatBox.appendChild(errorMsg);
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      if (chatBox) {
        const errorMsg = document.createElement("div");
        errorMsg.className = "chat-message bot error";
        errorMsg.textContent = "Connection error. Please try again.";
        chatBox.appendChild(errorMsg);
      }
    }
  };

  // Check if chatBox exists for conversation display
  if (chatBox) {
    chatBox.addEventListener("DOMContentLoaded", () => {
      // Load conversation history if available
      loadChatHistory();
    });
  }

  // Send message on Enter key
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendChatMsg();
    }
  });

  // Load chat history
  async function loadChatHistory() {
    try {
      const user = AuthAPI.getCurrentUser();
      const customerId = user?.id || "PAT999";

      const history = await ChatAPI.getConversationHistory(customerId);

      if (history.status === "success" && history.data && chatBox) {
        chatBox.innerHTML = "";
        history.data.forEach((msg) => {
          const msgEl = document.createElement("div");
          msgEl.className = `chat-message ${msg.sender}`;
          msgEl.textContent = msg.text;
          chatBox.appendChild(msgEl);
        });
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    } catch (error) {
      console.error("Load history error:", error);
    }
  }
}
