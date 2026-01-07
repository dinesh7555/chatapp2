import { useEffect, useState } from "react";
import Topbar from "./Topbar";
import Sidebar from "./Sidebar";
import ChatWindow from "../chat/ChatWindow";
import "./layout.css";

import {
  startChat,
  sendMessage as sendMessageApi,
  getConversations,
  getChatHistory,
} from "../../api/chat";

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // chats keyed by conversation_id
  const [chats, setChats] = useState({});
  const [activeChatId, setActiveChatId] = useState(null);
  const [loadingChats, setLoadingChats] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // 🔹 Load conversations on page load
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const data = await getConversations();

        const formattedChats = {};
        data.forEach((c) => {
          formattedChats[c.conversation_id] = {
            title: c.title || "New Chat",
            messages: [],
          }; 
        });

        setChats(formattedChats);

        // auto-open latest chat
        if (data.length > 0) {
          setActiveChatId(data[0].conversation_id);
        }
      } catch (err) {
        console.error("Failed to load conversations", err);
      } finally {
        setLoadingChats(false);
      }
    };
  loadConversations();
  }, []);



  // 🔹 Load chat history when active chat changes
  useEffect(() => {
    if (!activeChatId) return;

    const loadHistory = async () => {
      try {
        const data = await getChatHistory(activeChatId);

        setChats((prev) => ({
          ...prev,
          [activeChatId]: {
            ...prev[activeChatId],
            messages: data.messages || [],
          },
        }));
      } catch (err) {
        console.error("Failed to load chat history", err);
      }
    };

    loadHistory();
  }, [activeChatId]);

  // 🔹 Create new chat
  const createNewChat = async () => {
    try {
      const data = await startChat();
      const id = data.conversation_id;

      setChats((prev) => ({
        ...prev,
        [id]: {
          title: "New Chat",
          messages: [],
        },
      }));

      setActiveChatId(id);
    } catch (err) {
      console.error(err);
      alert("Failed to start new chat");
    }
  };

  // 🔹 Send message
  const sendMessage = async (text) => {
    if (!text.trim() || !activeChatId) return;

    // user message immediately
    setChats(prev => ({
      ...prev,
      [activeChatId]: {
        ...prev[activeChatId],
        messages: [
          ...prev[activeChatId].messages,
          { role: "user", content: text },
        ],
      },
    }));

    setIsLoading(true);

    try {
      await sendMessageApi(activeChatId, text);

      // 🔥 single source of truth
      const history = await getChatHistory(activeChatId);

      setChats(prev => ({
        ...prev,
        [activeChatId]: {
          ...prev[activeChatId],
          messages: history.messages || [],
        },
      }));
    } catch (err) {
      console.error(err);
      alert("Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };





  if (loadingChats) {
    return <div className="loading-screen">Loading chats...</div>;
  }

  return (
    <div className="app-container">
      <Topbar
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
      />


      <div className={`body-container ${sidebarOpen ? "sidebar-open" : ""}`}>
        {/* 🔹 Click-outside backdrop */}
        {sidebarOpen && (
          <div
            className="sidebar-backdrop"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <Sidebar
          open={sidebarOpen}
          chats={chats}
          activeChatId={activeChatId}
          onSelectChat={setActiveChatId}
          onNewChat={createNewChat}
        />

        <main className="chat-container">
          <ChatWindow
            messages={
              activeChatId && chats[activeChatId]
                ? chats[activeChatId].messages
                : []
            }
            onSend={sendMessage}
            isLoading={isLoading}
          />
        </main>
      </div>
    </div>
  );
}

export default Layout;
