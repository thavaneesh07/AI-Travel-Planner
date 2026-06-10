import React, { useState, useEffect } from "react";
import { usePlanning } from "../hooks/usePlanning";
import { useAuth } from "../hooks/useAuth";
import { useTrip } from "../hooks/useTrip";
import { ChatInterface } from "../components/chat/ChatInterface";
import { ItineraryView } from "../components/itinerary/ItineraryView";
import { RouteMap } from "../components/map/RouteMap";
import { getExportPdfUrl } from "../api/tripsApi";

interface PlannerPageProps {
  onNavigateToSaved: () => void;
  onNavigateToLogin: () => void;
}

export const PlannerPage: React.FC<PlannerPageProps> = ({ onNavigateToSaved, onNavigateToLogin }) => {
  const { tripData, resetPlanning, planningstate } = usePlanning();
  const { saveTrip } = useTrip();
  const { isAuthenticated, logout, user, loadUser } = useAuth();
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [showMap, setShowMap] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  useEffect(() => {
    if (tripData && tripData.days && tripData.days.length > 0) {
      if (selectedDay === null || selectedDay > tripData.days.length) {
        setSelectedDay(1);
      }
    } else {
      setSelectedDay(null);
    }
  }, [tripData]);

  const getMapActivities = () => {
    if (!tripData) return [];
    if (selectedDay !== null) {
      const dayData = tripData.days.find(d => d.day === selectedDay);
      return dayData ? dayData.activities : [];
    }
    return tripData.days.flatMap(d => d.activities);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex flex-col">
      <nav className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200 px-6 py-4 flex items-center justify-between relative z-50">
        <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 flex items-center gap-2">
          <span>🌍</span> AI Travel Assistant
        </h1>
        <div className="flex items-center gap-4">
          <button
            onClick={onNavigateToSaved}
            className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold rounded-xl transition-all"
          >
            🎒 Saved Trips
          </button>
          {isAuthenticated ? (
            <>
              <span className="text-sm text-gray-500 font-medium">👤 {user?.email}</span>
              <button
                onClick={() => {
                  logout();
                  resetPlanning();
                }}
                className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 font-bold rounded-xl transition-all"
              >
                Sign Out
              </button>
            </>
          ) : (
            <button
              onClick={onNavigateToLogin}
              className="px-5 py-2.5 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-bold rounded-xl shadow-md transition-all"
            >
              Sign In
            </button>
          )}
        </div>
      </nav>

      <div className="flex-1 flex flex-col lg:flex-row gap-6 p-6 max-w-[1600px] w-full mx-auto overflow-hidden">
        {/* Left Column: Chat Interface */}
        <div className="w-full lg:w-[450px] shrink-0 flex flex-col space-y-4">
          <ChatInterface />
          <button
            onClick={async () => {
              if (tripData && !tripData.tripid) {
                try {
                  await saveTrip(tripData);
                } catch (e) {
                  console.error("Auto-saving active itinerary failed:", e);
                }
              }
              resetPlanning();
              setSelectedDay(null);
            }}
            className="w-full py-3.5 bg-white hover:bg-blue-50 text-blue-600 border border-dashed border-blue-300 font-extrabold rounded-2xl shadow-sm hover:shadow transition-all duration-200 cursor-pointer flex items-center justify-center gap-2"
          >
            <span>✨</span> New Travel Itinerary
          </button>
        </div>

        {/* Right Column: Map & Step-by-Step Itinerary */}
        <div className="flex-1 flex flex-col space-y-6 overflow-y-auto max-h-[calc(100vh-140px)] pr-2">
          {tripData || planningstate?.entities?.destination ? (
            <>
              {tripData ? (
                <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-gray-50">
                  <span className="text-gray-500 text-sm font-semibold">
                    🗺️ Map visualization matches active itinerary
                  </span>
                  {tripData.tripid && (
                    <a
                      href={getExportPdfUrl(tripData.tripid)}
                      target="_blank"
                      rel="noreferrer"
                      className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white font-bold rounded-xl shadow-sm transition-all"
                    >
                      📄 Export PDF Itinerary
                    </a>
                  )}
                </div>
              ) : (
                <div className="bg-white p-5 rounded-3xl shadow-sm border border-gray-100 flex flex-col space-y-2">
                  <h3 className="text-xl font-extrabold text-gray-800 flex items-center gap-2">
                    <span>📍</span> Destination Detected: <span className="text-blue-600 capitalize">{planningstate.entities.destination}</span>
                  </h3>
                  <p className="text-sm text-gray-500 font-medium">
                    We are building your custom trip. Keep chatting on the left to complete the missing details!
                  </p>
                </div>
              )}
              
              <button
                onClick={() => setShowMap(!showMap)}
                className="w-full flex items-center justify-between p-4 bg-white border border-gray-100 rounded-3xl shadow-sm hover:border-blue-400 hover:shadow-md transition-all duration-200 cursor-pointer font-bold text-gray-700"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">🗺️</span>
                  <span>Map based guide</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-3 py-1 bg-blue-50 text-blue-600 rounded-full font-extrabold uppercase tracking-wider">
                    {showMap ? "Hide Map" : "View Map"}
                  </span>
                  <span
                    className="text-gray-400 transition-transform duration-200 text-xs"
                    style={{ transform: showMap ? "rotate(180deg)" : "rotate(0deg)" }}
                  >
                    ▼
                  </span>
                </div>
              </button>

              {showMap && (
                <div className="animate-fadeIn w-full">
                  <RouteMap
                    destination={tripData?.destination || planningstate?.entities?.destination}
                    activities={getMapActivities()}
                  />
                </div>
              )}
              
              {tripData && (
                <ItineraryView
                  trip={tripData}
                  selectedDay={selectedDay}
                  onSelectDay={setSelectedDay}
                />
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-[500px] bg-white rounded-3xl shadow-sm border border-gray-100 p-8 text-center space-y-4">
              <span className="text-6xl animate-bounce">✈️</span>
              <h3 className="text-2xl font-bold text-gray-800">Start Planning Your Dream Journey</h3>
              <p className="text-gray-500 max-w-md">
                Chat with the AI Travel Assistant on the left to specify your destination, dates, budget, and travel preferences!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
