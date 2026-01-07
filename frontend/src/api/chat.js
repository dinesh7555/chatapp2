const API_BASE = "http://localhost:8000";
import { handleAuthError } from "./http";

function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// 1️⃣ Start a new chat
export async function startChat() {
  const res = await fetch(`${API_BASE}/chat/start`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  handleAuthError(res);
  if (!res.ok) {
    throw new Error("Failed to start chat");
  }

  return res.json();
}

// 2️⃣ Send message
export async function sendMessage(conversationId, message) {
  const res = await fetch(`${API_BASE}/chat/message`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
  });
  handleAuthError(res);
  if (!res.ok) {
    throw new Error("Failed to send message");
  }
   
  const data =await res.json();
  return {
    role:"assistant",
    content : data.assistant_message,
  };
}

// 3️⃣ Fetch chat history
export async function getChatHistory(conversationId) {
  const res = await fetch(
    `${API_BASE}/chat/history/${conversationId}`,
    {
      headers: getAuthHeaders(),
    }
  );
  handleAuthError(res);
  if (!res.ok) {
    throw new Error("Failed to fetch chat history");
  }

  return res.json();
}

// 4️⃣ Fetch all conversations
export async function getConversations() {
  const res = await fetch(`${API_BASE}/chat/conversations`, {
    headers: getAuthHeaders(),
  });
  handleAuthError(res);
  if (!res.ok) {
    throw new Error("Failed to fetch conversations");
  }

  return res.json();
}
