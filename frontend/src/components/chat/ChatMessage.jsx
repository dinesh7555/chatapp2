import ReactMarkdown from "react-markdown";

function ChatMessage({ role, content }) {
  return (
    <div className={`message ${role}`}>
      <div className="message-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}

export default ChatMessage;
