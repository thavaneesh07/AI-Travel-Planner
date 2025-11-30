import React, { useState, useRef, useEffect } from "react";
import { postChat } from "../services/api";

function ChatPanel({ onAction }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! 👋 I'm your AI travel assistant. How can I help today?" }
  ]);
  const [loading, setLoading] = useState(false);

  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMsg = { role: "user", text: message };
    setMessages(prev => [...prev, userMsg]);
    setMessage("");
    setLoading(true);

    try {
      const res = await postChat({ messages: [...messages, userMsg] });

      if (res?.assistant) {
        // show assistant reply
        setMessages(prev => [
          ...prev,
          { role: "assistant", text: res.assistant.text }
        ]);

        // 🔥 PARTIAL update (modify itinerary)
        if (res.assistant.action === "modify_itinerary" && res.assistant.changes) {
          window.dispatchEvent(
            new CustomEvent("itineraryChanges", {
              detail: res.assistant.changes
            })
          );
        }

        // 🔥 Trigger frontend action
        if (res.assistant.action && onAction) {
          onAction(res.assistant.action);
        }

      } else {
        setMessages(prev => [
          ...prev,
          { role: "assistant", text: "Hmm, I didn't understand that." }
        ]);
      }

    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", text: "❌ Server error. Try again later." }
      ]);
    }

    setLoading(false);
  };

  const onKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div
      style={{
        width: "32%",
        height: "100vh",
        position: "fixed",
        right: 0,
        top: 0,
        background: "white",
        borderLeft: "1px solid #eee",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h2 style={{ fontSize: "22px", fontWeight: "bold", marginBottom: "10px" }}>
        💬 AI Travel Assistant
      </h2>

      {/* CHAT WINDOW */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: "auto",
          border: "1px solid #ddd",
          padding: "10px",
          borderRadius: "10px",
          background: "#fafafa",
          marginBottom: "15px"
        }}
      >
        {messages.map((m, idx) => (
          <div key={idx} style={{ textAlign: m.role === "user" ? "right" : "left", marginBottom: "10px" }}>
            <div
              style={{
                display: "inline-block",
                padding: "10px 14px",
                borderRadius: "10px",
                background: m.role === "user" ? "#007bff" : "#eaeaea",
                color: m.role === "user" ? "white" : "black",
                maxWidth: "80%",
                whiteSpace: "pre-wrap"
              }}
            >
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ fontStyle: "italic", color: "gray" }}>
            Assistant is typing...
          </div>
        )}
      </div>

      {/* INPUT AREA */}
      <div style={{ display: "flex", gap: "10px" }}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={onKeyPress}
          placeholder="Ask something..."
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            height: "60px",
            resize: "none"
          }}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            padding: "0 20px",
            background: "#007bff",
            color: "white",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
            height: "60px"
          }}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatPanel;
