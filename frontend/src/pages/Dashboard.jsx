// src/pages/Dashboard.jsx
import React, { useState } from "react";
import { planTrip } from "../services/api";
import WeatherChart from "../components/WeatherChart";
import BudgetChart from "../components/BudgetChart";
import MapView from "../components/MapView";
import Timeline from "../components/Timeline";



function Dashboard() {
  const [message, setMessage] = useState("");
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [showBudget, setShowBudget] = useState(false);



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
             activities={
          selectedDay
              ? [
              tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)
              ?.morning,
              tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)
              ?.afternoon,
              tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)
              ?.evening,
            ].filter(Boolean)
          : tripData.generated_itinerary?.days.flatMap((d) => [
          d.morning,
          d.afternoon,
          d.evening,
        ])
  }
/>
          <Timeline
            days={tripData.generated_itinerary?.days}
            selectedDay={selectedDay}
            onDaySelect={setSelectedDay}
          />

          {/* 🟢 Reset Button */}
          <div className="flex justify-end mb-4">
          <button
              onClick={() => setSelectedDay(null)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
          >
           Show All Days
           </button>
          </div>
          {/* 💰 Collapsible Budget Summary */}
<div className="mt-8 bg-gray-50 p-6 rounded-xl shadow-inner">
  {/* Header with toggle button */}
  <div
    className="flex justify-between items-center cursor-pointer"
    onClick={() => setShowBudget(!showBudget)}
  >
    <h3 className="text-2xl font-bold text-green-700">
      💵 Budget Summary
    </h3>
    <span
      className={`text-green-700 text-xl transform transition-transform duration-300 ${
        showBudget ? "rotate-180" : ""
      }`}
    >
      ⬇️
    </span>
  </div>

  {/* Animated collapsible section */}
  <div
    className={`transition-all duration-500 overflow-hidden ${
      showBudget ? "max-h-[500px] opacity-100 mt-4" : "max-h-0 opacity-0"
    }`}
  >
    {/* Daily breakdown */}
    <ul className="space-y-2">
      {tripData.generated_itinerary?.days?.map((day) => (
        <li
          key={day.day}
          className="flex justify-between border-b border-gray-200 pb-1 text-gray-800"
        >
          <span>
            Day {day.day}: {day.date}
          </span>
          <span className="font-semibold text-green-600">
            ${day.estimated_cost}
          </span>
        </li>
      ))}
    </ul>

    {/* Total budget */}
    <p className="mt-4 text-right text-xl font-bold text-green-700">
      Total Estimated Budget: $
      {tripData.generated_itinerary?.total_estimated_cost}
    </p>
  </div>
</div>


          <WeatherChart days={tripData.generated_itinerary?.days} />
           <BudgetChart days={tripData.generated_itinerary?.days} />

        </div>
      )}
    </div>
  );
}

export default Dashboard;
