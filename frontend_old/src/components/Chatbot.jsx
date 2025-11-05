import React, { useState } from "react";
import { parseMessage, generateItinerary } from "../services/api";

function Chatbot() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setError(null);

    try {
      // 1️⃣ Parse the user input
      const parsed = await parseMessage(message);
      setResponse(parsed);

      // 2️⃣ Generate itinerary from parsed data
      const itineraryData = await generateItinerary({
        destination: parsed.destination,
        start_date: parsed.start_date,
        end_date: parsed.end_date,
        budget: parsed.budget,
        user_profile: parsed.user_profile,
        interests: parsed.interests || [],
      });
      setItinerary(itineraryData);
    } catch (err) {
      console.error(err);
      setError("Failed to connect to the backend. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Travel Chatbot 🤖</h1>

      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="e.g., Plan a solo trip to Paris Oct 1–7 2025, budget 1500"
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "10px",
          border: "1px solid #ccc",
          borderRadius: "5px",
        }}
      />
      <button
        onClick={sendMessage}
        disabled={loading}
        style={{
          padding: "10px 20px",
          background: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        {loading ? "Thinking..." : "Send"}
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "10px" }}>{error}</p>
      )}

      {response && (
        <div
          style={{
            marginTop: "20px",
            border: "1px solid #ddd",
            padding: "10px",
            borderRadius: "5px",
          }}
        >
          <h3>🧭 Parsed Trip Info</h3>
          <p><strong>Destination:</strong> {response.destination}</p>
          <p><strong>Dates:</strong> {response.start_date} → {response.end_date}</p>
          <p><strong>Budget:</strong> ${response.budget}</p>
          <p><strong>Profile:</strong> {response.user_profile}</p>
          <p><strong>Interests:</strong> {response.interests?.join(", ")}</p>
        </div>
      )}

      {itinerary && (
        <div
          style={{
            marginTop: "20px",
            border: "1px solid #ddd",
            padding: "10px",
            borderRadius: "5px",
          }}
        >
          <h3>📅 Generated Itinerary</h3>
          <p><strong>Total Estimated Cost:</strong> ${itinerary.total_estimated_cost}</p>
          {itinerary.days.map((day) => (
            <div key={day.day} style={{ marginTop: "10px" }}>
              <strong>Day {day.day} ({day.date})</strong>
              <p>🌅 Morning: {day.morning}</p>
              <p>☀️ Afternoon: {day.afternoon}</p>
              <p>🌙 Evening: {day.evening}</p>
              <p>💰 Cost: ${day.estimated_cost}</p>
              {day.weather && (
                <p>🌦️ Weather: {day.weather.temp}°C, {day.weather.desc}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Chatbot;
