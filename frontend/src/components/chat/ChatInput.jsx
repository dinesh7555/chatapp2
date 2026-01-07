import { useState } from "react";

function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="chat-input">
      <input
        type="text"
        placeholder="Send a message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
          }
        }}

      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}

export default ChatInput;
