import React, { useState, useRef, useEffect } from "react";
import { postChat } from "../services/api";  // NEW unified chat endpoint

function Chatbot() {
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
    setMessages((prev) => [...prev, userMsg]);
    setMessage("");
    setLoading(true);

    try {
      const res = await postChat({ messages: [...messages, userMsg] });

      // Expected format:
      // { assistant: { text: "...", action?: { type: "...", ... } } }

      if (res?.assistant) {
        setMessages((prev) => [...prev, { role: "assistant", text: res.assistant.text }]);

        // Support actions like show_plan, etc.
        if (res.assistant.action) {
          setMessages((prev) => [
            ...prev,
            {
              role: "system",
              text: "🔧 ACTION TRIGGERED: " + JSON.stringify(res.assistant.action, null, 2)
            }
          ]);
        }

      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: "Hmm, I couldn't understand that. Try again?" }
        ]);
      }

    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "❌ Error connecting to server. Try again later." }
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
    <div style={{ width: "70%", margin: "0 auto", padding: "20px", fontFamily: "Arial" }}>
      <h1 style={{ textAlign: "center" }}>AI Travel Chat 🤖✈️</h1>

      <div
        ref={scrollRef}
        style={{
          height: "350px",
          overflowY: "auto",
          border: "1px solid #ccc",
          padding: "10px",
          borderRadius: "10px",
          background: "#fafafa",
          marginBottom: "15px"
        }}
      >
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: "12px",
              textAlign: m.role === "user" ? "right" : "left"
            }}
          >
            <div
              style={{
                display: "inline-block",
                background: m.role === "user" ? "#007bff" : "#eaeaea",
                color: m.role === "user" ? "white" : "black",
                padding: "10px 14px",
                borderRadius: "10px",
                maxWidth: "70%",
                whiteSpace: "pre-wrap",
              }}
            >
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ textAlign: "left", fontStyle: "italic", color: "gray" }}>
            Assistant is typing...
          </div>
        )}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={onKeyPress}
          placeholder="Ask me anything — e.g., 'Plan a 5-day Tokyo trip, budget 2000'"
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            resize: "none",
            height: "60px"
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

export default Chatbot;
