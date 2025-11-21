// src/pages/Dashboard.jsx
import React, { useState } from "react";
import { planTrip, getSuggestions, getHotels } from "../services/api";
import WeatherChart from "../components/WeatherChart";
import MapView from "../components/MapView";
import Timeline from "../components/Timeline";
import HotelList from "../components/HotelList";

// NEW
import ChatPanel from "../components/ChatPanel";

function Dashboard() {
  const [message, setMessage] = useState("");
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [hotels, setHotels] = useState([]);

  // NEW — for showing chat panel
  const [showChat, setShowChat] = useState(true);

  const handlePlanTrip = async () => {
    if (!message.trim()) return;
    setLoading(true);

    try {
      const res = await planTrip(message);

      const hotelResponse = await getHotels(res);
      res.hotels = hotelResponse.hotels;
      setHotels(hotelResponse.hotels);

      setTripData(res);

      if (res?.parsed_query?.destination && res?.parsed_query?.budget) {
        setLoadingSuggestions(true);
        try {
          const sug = await getSuggestions(res);
          setSuggestions(sug.suggestions || []);
        } catch (err) {
          console.error("Suggestion error:", err);
        } finally {
          setLoadingSuggestions(false);
        }
      }
    } catch (error) {
      console.error("Main Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 p-6 flex">

      {/* LEFT MAIN DASHBOARD CONTENT */}
      <div
        className={`
          transition-all duration-300
          ${showChat ? "w-2/3" : "w-full"}
          mx-auto
        `}
      >
        <h1 className="text-4xl font-bold text-blue-800 mb-6 flex items-center gap-2">
          🌍 AI Travel Dashboard
        </h1>

        {/* CHAT TOGGLE BUTTON */}
        <button
          onClick={() => setShowChat(!showChat)}
          className="mb-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700 transition"
        >
          {showChat ? "Close Chat" : "💬 Open Chat"}
        </button>

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

        {tripData && (
          <div className="bg-white shadow-lg rounded-2xl p-8 w-full border border-gray-100 space-y-8">

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

            {/* MAP VIEW */}
            <MapView
              destination={tripData.parsed_query?.destination}
              activities={
  selectedDay
    ? [
        tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.morning?.name,
        tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.afternoon?.name,
        tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.evening?.name,
      ].filter(Boolean)
    : tripData.generated_itinerary?.days.flatMap((d) => [
        d.morning?.name,
        d.afternoon?.name,
        d.evening?.name
      ]).filter(Boolean)
}

              hotels={tripData.hotels}
            />

            {/* Timeline */}
            <Timeline
              days={tripData.generated_itinerary?.days}
              selectedDay={selectedDay}
              onDaySelect={setSelectedDay}
            />

            {/* Show All Days */}
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

          {/* 🤖 Smart AI Suggestions */}
<div className="mt-10 bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-2xl shadow-xl border border-yellow-300">
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-2xl font-bold text-yellow-700 flex items-center gap-2">
      🤖 Smart AI Suggestions
    </h3>

    {/* Small "thinking" animation when loading */}
    {loadingSuggestions && (
      <div className="animate-pulse text-yellow-600 font-semibold">
        Thinking...
      </div>
    )}
  </div>

  {/* Suggestions list */}
  {loadingSuggestions ? (
    <p className="text-gray-600 italic">Generating personalized insights...</p>
  ) : suggestions.length > 0 ? (
    <ul className="space-y-4">
      {suggestions.map((tip, idx) => (
        <li
          key={idx}
          className="flex items-start gap-3 bg-white/80 p-3 rounded-xl shadow-sm border border-yellow-200 hover:shadow-md transition cursor-default"
        >
          <span className="text-xl">⭐</span>
          <p className="text-gray-800 leading-relaxed">{tip}</p>
        </li>
      ))}
    </ul>
  ) : (
    <p className="text-gray-600 italic">
      No AI suggestions available yet — try planning your trip again!
    </p>
  )}
</div>

            {/* Hotels */}
            <h2 className="text-2xl font-bold text-blue-700 mt-10">🏨 Recommended Hotels</h2>
            <HotelList hotels={hotels} />

            {/* Weather Chart */}
            <div className="pt-4 border-t border-gray-200">
              <h2 className="text-2xl font-bold text-blue-700 mt-10">🌦️ Weather Chart</h2>
              <WeatherChart days={tripData.generated_itinerary?.days} />
            </div>
          </div>
        )}
      </div>

      {/* RIGHT CHAT PANEL */}
      {showChat && (
        <div className="w-1/3">
          <ChatPanel />
        </div>
      )}
    </div>
  );
}

export default Dashboard;
