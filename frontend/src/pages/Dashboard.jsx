// src/pages/Dashboard.jsx
import React, { useState } from "react";
import { planTrip, getSuggestions, getHotels } from "../services/api";
import WeatherChart from "../components/WeatherChart";
import MapView from "../components/MapView";
import Timeline from "../components/Timeline";
import HotelList from "../components/HotelList";
import ChatPanel from "../components/ChatPanel";

function Dashboard() {
  const [message, setMessage] = useState("");
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [hotels, setHotels] = useState([]);
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
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 flex gap-6 overflow-hidden">
      {/* Subtle Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-32 h-32 bg-blue-200 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-purple-200 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-indigo-200 rounded-full blur-2xl animate-pulse delay-500"></div>
      </div>

      {/* Floating Chat Toggle Button - Top Right */}
      <button
        onClick={() => setShowChat(!showChat)}
        className="fixed top-6 right-6 z-50 bg-gradient-to-r from-blue-500 to-purple-500 text-white p-4 rounded-full shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-300 hover:rotate-12"
        title={showChat ? "Close Chat" : "Open Chat"}
      >
        {showChat ? "✖️" : "💬"}
      </button>

      {/* LEFT MAIN DASHBOARD CONTENT */}
      <div
        className={`transition-all duration-500 ease-in-out relative z-10 ${
          showChat ? "w-2/3" : "w-full"
        } space-y-8`}
      >
        {/* Header Section */}
        <div className="text-center animate-fade-in">
          <h1 className="text-5xl font-extrabold mb-4 flex items-center justify-center gap-3 hover:scale-105 transition-transform duration-500">
            <span className="animate-bounce">🌍</span>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 animate-pulse">
              AI Travel Dashboard
            </span>
          </h1>
          <p className="text-lg text-gray-600 italic">Plan your dream trip with AI-powered insights</p>
        </div>

        {/* Input Section */}
        <div className="flex w-full max-w-4xl mx-auto shadow-2xl rounded-full overflow-hidden bg-white hover:shadow-3xl transition-shadow duration-300">
          <input
            type="text"
            className="flex-1 p-4 text-lg border-0 focus:ring-4 focus:ring-blue-300 outline-none placeholder-gray-400 transition-all duration-300"
            placeholder="e.g. Plan a solo trip to Tokyo for 5 days in Dec, budget 2000, love food and art"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button
            onClick={handlePlanTrip}
            className="px-8 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-300 hover:shadow-lg transform hover:scale-105"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Planning...
              </div>
            ) : (
              "Plan Trip"
            )}
          </button>
        </div>

        {tripData && (
          <div className="bg-white shadow-2xl rounded-3xl p-10 space-y-10 border border-gray-100 animate-slide-up">
            {/* Parsed Trip Info */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-3xl font-bold text-purple-700 mb-6 flex items-center gap-3">
                🌸 Parsed Trip Info
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-800">
                <div className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <p className="flex items-center gap-2">
                    <span className="text-xl">📍</span>
                    <strong>Destination:</strong> {tripData.parsed_query?.destination}
                  </p>
                </div>
                <div className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <p className="flex items-center gap-2">
                    <span className="text-xl">💰</span>
                    <strong>Budget:</strong> ${tripData.parsed_query?.budget}
                  </p>
                </div>
                <div className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <p className="flex items-center gap-2">
                    <span className="text-xl">🗓️</span>
                    <strong>Dates:</strong> {tripData.parsed_query?.start_date} → {tripData.parsed_query?.end_date}
                  </p>
                </div>
                <div className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <p className="flex items-center gap-2">
                    <span className="text-xl">🧍</span>
                    <strong>Profile:</strong> {tripData.parsed_query?.user_profile}
                  </p>
                </div>
                <div className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 col-span-1 md:col-span-2">
                  <p className="flex items-center gap-2">
                    <span className="text-xl">🎨</span>
                    <strong>Interests:</strong> {tripData.parsed_query?.interests?.join(", ")}
                  </p>
                </div>
              </div>
            </div>

            {/* Map View */}
            <div className="rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300">
              <MapView
                destination={tripData.parsed_query?.destination}
                activities={
                  selectedDay
                    ? [
                        tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.morning,
                        tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.afternoon,
                        tripData.generated_itinerary?.days.find((d) => d.day === selectedDay)?.evening,
                      ].filter(Boolean)
                    : tripData.generated_itinerary?.days.flatMap((d) => [
                        d.morning,
                        d.afternoon,
                        d.evening
                      ]).filter(Boolean)
                }
                hotels={tripData.hotels}
              />
            </div>

            {/* Timeline */}
            <div className="bg-gray-50 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300">
              <Timeline
                days={tripData.generated_itinerary?.days}
                selectedDay={selectedDay}
                onDaySelect={setSelectedDay}
              />
              <div className="flex justify-end mt-4">
                <button
                  onClick={() => setSelectedDay(null)}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 transition-all duration-300 hover:shadow-md transform hover:scale-105"
                >
                  Show All Days
                </button>
              </div>
            </div>

            {/* Trip Budget Overview */}
            {tripData.generated_itinerary && (
              <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-8 rounded-2xl shadow-lg border border-indigo-200 hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-3xl font-bold text-indigo-700 mb-6 flex items-center gap-3">
                  💰 Trip Budget Overview
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-gray-800">
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                    <span className="block font-semibold text-gray-600">Total Budget</span>
                    <span className="text-2xl font-bold text-indigo-700">
                      ${tripData.parsed_query?.budget}
                    </span>
                  </div>
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                    <span className="block font-semibold text-gray-600">Estimated Total Cost</span>
                    <span className="text-2xl font-bold text-blue-700">
                      ${tripData.generated_itinerary?.total_estimated_cost}
                    </span>
                  </div>
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                    <span className="block font-semibold text-gray-600">Remaining Budget</span>
                    <span className="text-2xl font-bold text-purple-600">
                      $
                      {(
                        tripData.parsed_query?.budget -
                        tripData.generated_itinerary?.total_estimated_cost
                      ).toFixed(2)}
                    </span>
                  </div>
                  <div className="text-center bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                    <span className="block font-semibold text-gray-600">Avg. Daily Spend</span>
                    <span className="text-2xl font-bold text-blue-600">
                      $
                      {(
                        tripData.generated_itinerary?.total_estimated_cost /
                        tripData.generated_itinerary?.days.length
                      ).toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className="mt-8">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
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
                  <div className="w-full bg-gray-200 h-4 rounded-full overflow-hidden">
                    <div
                      className="h-4 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-1000 ease-in-out hover:shadow-inner"
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

            {/* Smart AI Suggestions */}
            <div className="bg-gradient-to-br from-yellow-50 to-orange-100 p-8 rounded-2xl shadow-lg border border-yellow-300 hover:shadow-xl transition-shadow duration-300">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-3xl font-bold text-yellow-700 flex items-center gap-3">
                  🤖 Smart AI Suggestions
                </h3>
                {loadingSuggestions && (
                  <div className="animate-pulse text-yellow-600 font-semibold flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-yellow-600 border-t-transparent rounded-full animate-spin"></div>
                    Thinking...
                  </div>
                )}
              </div>
              {loadingSuggestions ? (
                <p className="text-gray-600 italic">Generating personalized insights...</p>
              ) : suggestions.length > 0 ? (
                <ul className="space-y-4">
                  {suggestions.map((tip, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-4 bg-white/90 p-4 rounded-xl shadow-sm border border-yellow-200 hover:shadow-md transition-all duration-300 hover:scale-102"
                    >
                      <span className="text-2xl animate-pulse">⭐</span>
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
            <div className="bg-gray-50 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-3xl font-bold text-blue-700 mb-6 flex items-center gap-3">
                🏨 Recommended Hotels
              </h2>
              <HotelList hotels={hotels} />
            </div>

            {/* Weather Chart */}
            <div className="bg-gray-50 p-6 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-3xl font-bold text-blue-700 mb-6 flex items-center gap-3">
                🌦️ Weather Chart
              </h2>
              <WeatherChart days={tripData.generated_itinerary?.days} />
            </div>
          </div>
        )}
      </div>

      {/* RIGHT CHAT PANEL */}
      {showChat && (
        <div className="w-1/3 bg-white shadow-2xl rounded-3xl overflow-hidden animate-slide-in-right">
          <ChatPanel />
        </div>
      )}
    </div>
  );
}

export default Dashboard;
