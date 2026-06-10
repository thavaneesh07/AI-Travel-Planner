import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import MapView from "./MapView";
import { v4 as uuidv4 } from "uuid"; // Needs npm install uuid

function Chatbot() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! 👋 I'm your AI travel assistant. How can I help today?" }
  ]);
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [budgetInfo, setBudgetInfo] = useState(null);
  const [sessionId] = useState(uuidv4()); // Maintain conversation context

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
      const response = await axios.post("http://127.0.0.1:8000/api/generate", {
        session_id: sessionId,
        message: userMsg.text,
        history: messages
      });

      const data = response.data;

      if (data.status === "needs_more_info") {
        setMessages((prev) => [...prev, { role: "assistant", text: data.question }]);
      } else if (data.status === "success") {
        if (data.intent === "plan_trip" && data.trip) {
          setMessages((prev) => [...prev, { role: "assistant", text: "Your trip is ready! Take a look below." }]);
          setItinerary(data.trip.itinerary);
          setBudgetInfo(data.trip.budget_info);
        } else if (data.answer) {
          setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
        }
      }

    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "❌ Error connecting to the AI brain. Try again later." }
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

      {itinerary && (
        <div style={{ marginTop: 20 }}>
          <h2>Planned Itinerary — {itinerary.destination}</h2>
          
          {budgetInfo && (
            <div style={{ background: '#e0f7fa', padding: 15, borderRadius: 8, marginBottom: 15 }}>
              <h4>💰 Budget Summary ({budgetInfo.comfort_level})</h4>
              <p>Score: {budgetInfo.score}/10 | Daily PP: ${budgetInfo.daily_budget_per_person}</p>
            </div>
          )}

          <MapView
            activities={itinerary.days.flatMap(d => [
              { name: d.morning.name || d.morning, lat: d.morning.lat, lon: d.morning.lon, type: 'morning' },
              { name: d.afternoon.name || d.afternoon, lat: d.afternoon.lat, lon: d.afternoon.lon, type: 'afternoon' },
              { name: d.evening.name || d.evening, lat: d.evening.lat, lon: d.evening.lon, type: 'evening' },
            ])}
            destination={itinerary.destination}
            hotels={itinerary.hotels || []}
          />

          {itinerary.days.map((d) => (
            <div key={d.date} style={{ border: '1px solid #ddd', padding: 10, margin: '8px 0' }}>
              <h3>Day {d.day} — {d.date}</h3>
              <p><strong>Morning:</strong> {typeof d.morning === 'string' ? d.morning : d.morning.name}</p>
              <p><strong>Afternoon:</strong> {typeof d.afternoon === 'string' ? d.afternoon : d.afternoon.name}</p>
              <p><strong>Evening:</strong> {typeof d.evening === 'string' ? d.evening : d.evening.name}</p>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: "10px" }}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={onKeyPress}
          placeholder="Ask me anything about travel, or say 'Plan a trip to Tokyo'"
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
