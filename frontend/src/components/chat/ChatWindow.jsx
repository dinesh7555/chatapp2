import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import "./chat.css";

function ChatWindow({ messages = [], onSend, isLoading }) {
  const bottomRef = useRef(null);

  // 🔥 auto-scroll when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.length === 0 && !isLoading && (
          <div className="empty-chat">Start a conversation 👋</div>
        )}

        {messages.map((msg, index) => (
          <ChatMessage
            key={`${msg.role}-${index}`}
            role={msg.role}
            content={msg.content}
          />
        ))}

        {/* 🔹 Loading indicator */}
        {isLoading && (
          <div className="message assistant typing">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}

        {/* 🔹 scroll target */}
        <div ref={bottomRef} />
      </div>

      <ChatInput onSend={onSend} />
    </div>
  );
}

export default ChatWindow;
