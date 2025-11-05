// src/pages/Dashboard.jsx
import React, { useState } from "react";
import { planTrip } from "../services/api";

function Dashboard() {
  const [message, setMessage] = useState("");
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePlanTrip = async () => {
    if (!message.trim()) return;
    setLoading(true);
    try {
      const res = await planTrip(message);
      setTripData(res);
    } catch (error) {
      console.error("Error fetching trip data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex flex-col items-center p-8 font-sans">
      <h1 className="text-4xl font-extrabold text-blue-700 mb-6 drop-shadow-sm">
        🌍 AI Travel Dashboard
      </h1>

      {/* --- Input Section --- */}
      <div className="flex w-full max-w-2xl mb-10 shadow-lg rounded-lg overflow-hidden border border-gray-200">
        <input
          type="text"
          className="flex-1 p-3 text-lg border-none outline-none"
          placeholder="e.g. Plan a solo trip to Paris, Nov 5–8 2025, budget 1500, food and art"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button
          onClick={handlePlanTrip}
          className={`px-6 py-2 text-white font-semibold transition-all ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
          disabled={loading}
        >
          {loading ? "Planning..." : "Plan Trip"}
        </button>
      </div>

      {/* --- Parsed Trip Info Card --- */}
      {tripData && (
        <div className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-3xl border border-gray-100 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">🧭</span> Parsed Trip Info
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-2 text-gray-700">
            <p><strong>🌆 Destination:</strong> {tripData.parsed_query?.destination}</p>
            <p><strong>💰 Budget:</strong> ${tripData.parsed_query?.budget}</p>
            <p><strong>🗓 Dates:</strong> {tripData.parsed_query?.start_date} → {tripData.parsed_query?.end_date}</p>
            <p><strong>🧍 Profile:</strong> {tripData.parsed_query?.user_profile}</p>
            <p className="sm:col-span-2"><strong>🎨 Interests:</strong> {tripData.parsed_query?.interests?.join(", ")}</p>
          </div>
        </div>
      )}

      {/* --- Itinerary Section --- */}
      {tripData && (
        <div className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-4xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="mr-2">🗓</span> Generated Itinerary
          </h2>

          <div className="grid gap-6">
            {tripData.generated_itinerary?.days?.map((day) => (
              <div
                key={day.day}
                className="bg-blue-50 border border-blue-200 p-6 rounded-xl shadow-sm hover:shadow-md transition-all"
              >
                <h3 className="text-xl font-semibold text-blue-800 mb-2">
                  Day {day.day} — {day.date}
                </h3>
                <p className="text-gray-700 mb-1">🌤 <strong>Weather:</strong> {day.weather?.temp}°C, {day.weather?.desc}</p>
                <p className="text-gray-700 mb-1">🌅 <strong>Morning:</strong> {day.morning}</p>
                <p className="text-gray-700 mb-1">🌇 <strong>Afternoon:</strong> {day.afternoon}</p>
                <p className="text-gray-700 mb-2">🌃 <strong>Evening:</strong> {day.evening}</p>
                <p className="text-green-700 font-medium">💰 Cost: ${day.estimated_cost}</p>
              </div>
            ))}
          </div>

          <p className="mt-8 text-lg font-semibold text-green-700 border-t border-gray-200 pt-4">
            💵 Total Estimated Cost: ${tripData.generated_itinerary?.total_estimated_cost}
          </p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
