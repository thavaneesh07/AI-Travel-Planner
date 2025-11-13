// src/pages/Dashboard.jsx
import React, { useState } from "react";
import { planTrip, getSuggestions } from "../services/api";
import WeatherChart from "../components/WeatherChart";
import MapView from "../components/MapView";
import Timeline from "../components/Timeline";


function Dashboard() {
  const [message, setMessage] = useState("");
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [showBudget, setShowBudget] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
const [loadingSuggestions, setLoadingSuggestions] = useState(false);




const handlePlanTrip = async () => {
  if (!message.trim()) return;
  setLoading(true);

  try {
    // 1️⃣ Fetch trip plan
    const res = await planTrip(message);
    setTripData(res);

    // 2️⃣ Fetch AI suggestions only when valid data exists
    if (res?.parsed_query?.destination && res?.parsed_query?.budget) {
      setLoadingSuggestions(true);
      try {
        const sug = await getSuggestions(res);
        setSuggestions(sug.suggestions || []);
      } catch (err) {
        console.error("Error fetching AI suggestions:", err);
      } finally {
        setLoadingSuggestions(false);
      }
    }
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
        <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-4xl border border-gray-100 space-y-8">
          {/* Parsed Trip Info */}
          <div>
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
            activities={
              selectedDay
                ? [
                    tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.morning,
                    tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.afternoon,
                    tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.evening,
                  ].filter(Boolean)
                : tripData.generated_itinerary?.days.flatMap((d) => [d.morning, d.afternoon, d.evening])
            }
          />

          {/* Timeline Section */}
          <Timeline
            days={tripData.generated_itinerary?.days}
            selectedDay={selectedDay}
            onDaySelect={setSelectedDay}
          />

          {/* 🟢 Reset Button */}
          <div className="flex justify-end">
            <button
              onClick={() => setSelectedDay(null)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Show All Days
            </button>
          </div>
          {/* 💰 Trip Budget Overview (themed in blue & purple) */}
{tripData.generated_itinerary && (
  <div className="mt-10 bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-2xl shadow-md border border-indigo-200">
    <h3 className="text-2xl font-bold text-indigo-700 mb-4 flex items-center gap-2">
      💰 Trip Budget Overview
    </h3>

    {/* Two-column summary */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-gray-800 text-sm sm:text-base">
      <div className="flex flex-col">
        <span className="font-semibold text-gray-600">Total Budget</span>
        <span className="text-lg font-bold text-indigo-700">
          ${tripData.parsed_query?.budget}
        </span>
      </div>

      <div className="flex flex-col">
        <span className="font-semibold text-gray-600">Estimated Total Cost</span>
        <span className="text-lg font-bold text-blue-700">
          ${tripData.generated_itinerary?.total_estimated_cost}
        </span>
      </div>

      <div className="flex flex-col">
        <span className="font-semibold text-gray-600">Remaining Budget</span>
        <span className="text-lg font-bold text-purple-600">
          $
          {(
            tripData.parsed_query?.budget -
            tripData.generated_itinerary?.total_estimated_cost
          ).toFixed(2)}
        </span>
      </div>

      <div className="flex flex-col">
        <span className="font-semibold text-gray-600">Avg. Daily Spend</span>
        <span className="text-lg font-bold text-blue-600">
          $
          {(
            tripData.generated_itinerary?.total_estimated_cost /
            tripData.generated_itinerary?.days.length
          ).toFixed(2)}
        </span>
      </div>
    </div>

    {/* Progress Bar */}
    <div className="mt-6">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>Used Budget</span>
        <span>
          {(
            (tripData.generated_itinerary?.total_estimated_cost /
              tripData.parsed_query?.budget) *
            100
          ).toFixed(0)}
          %
        </span>
      </div>
      <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden">
        <div
          className="h-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-700 ease-in-out"
          style={{
            width: `${
              (tripData.generated_itinerary?.total_estimated_cost /
                tripData.parsed_query?.budget) *
              100
            }%`,
          }}
        ></div>
      </div>
    </div>
  </div>
)}



          {/* 🌦️ Weather Chart */}
          <div className="pt-4 border-t border-gray-200">

            <WeatherChart days={tripData.generated_itinerary?.days} />
          </div>
          {/* 🧠 Smart AI Suggestions */}
<div className="mt-8 bg-yellow-50 p-6 rounded-2xl shadow-inner border border-yellow-200">
  <h3 className="text-2xl font-bold text-yellow-700 mb-4 flex items-center gap-2">
    🤖 Smart AI Suggestions
  </h3>

  {loadingSuggestions ? (
    <p className="text-gray-600 italic">Generating insights...</p>
  ) : suggestions.length > 0 ? (
    <ul className="space-y-3 text-gray-800 list-disc list-inside">
      {suggestions.map((tip, idx) => (
        <li key={idx}>{tip}</li>
      ))}
    </ul>
  ) : (
    <p className="text-gray-600 italic">
      No AI suggestions available yet — try re-planning your trip!
    </p>
  )}
</div>


        </div>
      )}
    </div>
  );
}

export default Dashboard;
