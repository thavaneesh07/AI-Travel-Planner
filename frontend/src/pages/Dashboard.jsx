// src/pages/Dashboard.jsx
import React, { useState } from "react";
import { planTrip } from "../services/api";
import WeatherChart from "../components/WeatherChart";
import BudgetChart from "../components/BudgetChart";
import MapView from "../components/MapView";



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
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 flex flex-col items-center p-6">
      <h1 className="text-4xl font-bold text-blue-800 mb-6 flex items-center gap-2">
        🌍 AI Travel Dashboard
      </h1>

      {/* Input Section */}
      <div className="flex w-full max-w-3xl mb-8">
        <input
          type="text"
          className="flex-1 p-3 border border-gray-300 rounded-l-lg shadow-sm focus:ring-2 focus:ring-blue-400 outline-none"
          placeholder="e.g. Plan a solo trip to Tokyo for 5 days in Dec, budget 2000, love food and art"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button
          onClick={handlePlanTrip}
          className="px-6 bg-blue-600 text-white font-semibold rounded-r-lg hover:bg-blue-700 transition"
        >
          {loading ? "Planning..." : "Plan Trip"}
        </button>
      </div>

      {/* Results Section */}
      {tripData && (
        <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-4xl border border-gray-100">
          {/* Parsed Trip Info */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-purple-700 mb-4 flex items-center gap-2">
              🌸 Parsed Trip Info
            </h2>
            <div className="grid grid-cols-2 gap-y-2 text-gray-800">
              <p><strong>📍 Destination:</strong> {tripData.parsed_query?.destination}</p>
              <p><strong>💰 Budget:</strong> ${tripData.parsed_query?.budget}</p>
              <p><strong>🗓 Dates:</strong> {tripData.parsed_query?.start_date} → {tripData.parsed_query?.end_date}</p>
              <p><strong>🧍 Profile:</strong> {tripData.parsed_query?.user_profile}</p>
              <p className="col-span-2">
                <strong>🎨 Interests:</strong> {tripData.parsed_query?.interests?.join(", ")}
              </p>
            </div>
          </div>

          {/* 🗺️ Map Section */}
          <MapView
          destination={tripData.parsed_query?.destination}
          activities={tripData.generated_itinerary?.days?.map(
          (d) => `${d.morning}, ${d.afternoon}, ${d.evening}`
          )}
        />


          {/* Itinerary Section */}
          <div>
            <h3 className="text-2xl font-bold text-blue-700 mb-4 flex items-center gap-2">
              📅 Generated Itinerary
            </h3>
            <ul className="space-y-4">
              {tripData.generated_itinerary?.days?.map((day) => (
                <li key={day.day} className="p-4 border border-gray-200 rounded-xl bg-blue-50">
                  <p className="font-semibold text-lg text-blue-900">
                    Day {day.day} — {day.date}
                  </p>
                  <p className="text-gray-700">
                    🌤 <strong>Weather:</strong> {day.weather?.temp}°C, {day.weather?.desc}
                  </p>
                  <p>🌅 <strong>Morning:</strong> {day.morning}</p>
                  <p>🌇 <strong>Afternoon:</strong> {day.afternoon}</p>
                  <p>🌃 <strong>Evening:</strong> {day.evening}</p>
                  <p className="font-semibold text-green-700 mt-1">
                    💸 Cost: ${day.estimated_cost}
                  </p>
                </li>
              ))}
            </ul>
            <p className="mt-6 text-xl font-semibold text-green-600 text-right">
              💵 Total Estimated Cost: ${tripData.generated_itinerary?.total_estimated_cost}
            </p>
            <WeatherChart days={tripData.generated_itinerary?.days} />
            <BudgetChart days={tripData.generated_itinerary?.days} />

          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
