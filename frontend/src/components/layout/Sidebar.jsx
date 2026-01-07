function Sidebar({ open, chats, activeChatId, onSelectChat, onNewChat }) {
  return (
    <aside className={`sidebar ${open ? "open" : ""}`}
    onClick={(e) => e.stopPropagation()}>
      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <div className="chat-list">
        {Object.entries(chats).map(([id, chat]) => (
          <div
            key={id}
            className={`chat-item ${id === activeChatId ? "active" : ""}`}
            onClick={() => onSelectChat(id)}
          >
            {chat.title}
          </div>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;
