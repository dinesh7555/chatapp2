import { useState } from "react";
import { apiRequest } from "../api/api";

import "./Chat.css";

function Chat({onLogout}) {
  const [conversationId, setConversationId] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  async function startChat() {
    const data = await apiRequest("/chat/start", "POST");
    setConversationId(data.conversation_id);
    setMessages([]);
  }

  async function sendMessage() {
    if (!message || !conversationId) return;

    const data = await apiRequest("/chat/message", "POST", {
      conversation_id: conversationId,
      message,
    });

    setMessages((prev) => [
      ...prev,
      { role: "user", content: data.user_message },
      { role: "assistant", content: data.assistant_message },
    ]);

    setMessage("");
  }
  

  return (
  <div className="chat-container">
    <div className="chat-header">
      <h2>Chat</h2>
      <button className="logout-button" type="button" onClick={onLogout}>Logout</button>
    </div>

    {!conversationId && (
      <button type="button" onClick={startChat}>Start New Chat</button>
    )}

    <div className="chat-box">
      {messages.map((m, i) => (
        <div key={i} className={`message ${m.role}`}>
          {m.content}
        </div>
      ))}
    </div>

    {conversationId && (
    <form
    className="chat-input"
    onSubmit={(e) => {
      e.preventDefault();   
      sendMessage();       
    }}
    >
    <input
      value={message}
      onChange={(e) => setMessage(e.target.value)}
      placeholder="Type a message..."
    />

    <button type="submit">Send</button>
    </form>
    )}

  </div>
  );

}

export default Chat;
