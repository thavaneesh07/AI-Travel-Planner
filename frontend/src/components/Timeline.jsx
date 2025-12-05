import React, { useState, useEffect } from "react";

function Timeline({ days = [], selectedDay, onDaySelect }) {
  const [localDays, setLocalDays] = useState(days);

  // When parent sends a brand-new itinerary
  useEffect(() => {
    setLocalDays(days);
  }, [days]);

  // Handle chatbot updates: full + partial
  useEffect(() => {
    // FULL itinerary replacement (all days)
    const fullUpdateHandler = (e) => {
      const data = e.detail;
      if (!data) return;

      // data can be {days:[...]} or just [...]
      setLocalDays(data.days || data);
    };

    // PARTIAL slot update (e.detail = { day2: { afternoon: "New name" } })
    const partialUpdateHandler = (e) => {
      const changes = e.detail;
      if (!changes) return;

      setLocalDays((prev) => {
        const updated = [...prev];

        Object.entries(changes).forEach(([dayKey, slotUpdates]) => {
          const dayIndex = parseInt(dayKey.replace("day", "")) - 1;
          if (!updated[dayIndex]) return;

          Object.entries(slotUpdates).forEach(([slot, newName]) => {
            const oldSlot = updated[dayIndex][slot] || {};

            // Preserve lat/lon/tags if they existed
            updated[dayIndex][slot] = {
              ...oldSlot,
              name: newName,
              tags: { modified_by_chat: true },
              activity_label: slot,
              lat: oldSlot.lat ?? null,
              lon: oldSlot.lon ?? null
            };
          });
        });

        return updated;
      });
    };

    window.addEventListener("itineraryUpdated", fullUpdateHandler);
    window.addEventListener("itineraryChanges", partialUpdateHandler);

    return () => {
      window.removeEventListener("itineraryUpdated", fullUpdateHandler);
      window.removeEventListener("itineraryChanges", partialUpdateHandler);
    };
  }, []);

  if (!localDays || localDays.length === 0) return null;

  const getDateForDay = (index) => {
    try {
      const start = new Date(
        localDays[0].date ||
        localDays[0].start_date ||
        localDays[0].iso_date
      );
      const result = new Date(start);
      result.setDate(start.getDate() + index);
      return result.toISOString().slice(0, 10);
    } catch {
      return "";
    }
  };

  return (
    <div className="relative">
      {/* Vertical Timeline Line */}
      <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-400 to-purple-400 rounded-full"></div>

      <div className="space-y-8">
        {localDays.map((day, i) => {
          const dateString = day.date || getDateForDay(i);
          const isSelected = selectedDay === day.day;

          return (
            <div
              key={day.day}
              onClick={() => onDaySelect(day.day)}
              className={`relative cursor-pointer ml-16 p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-500 transform hover:scale-105 border-l-4 ${
                isSelected
                  ? "border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg"
                  : "border-gray-300 hover:border-blue-300"
              }`}
            >
              {/* Timeline Dot */}
              <div
                className={`absolute -left-12 top-6 w-6 h-6 rounded-full border-4 border-white shadow-lg transition-all duration-300 ${
                  isSelected ? "bg-blue-500 animate-pulse" : "bg-gray-400"
                }`}
              ></div>

              {/* Day Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-xl text-blue-700 flex items-center gap-2">
                  <span className="text-2xl">📅</span>
                  Day {day.day} — {dateString}
                </h3>
                <div className="text-right">
                  <p className="text-lg font-semibold text-green-600 flex items-center gap-1">
                    <span>💸</span> ${day.estimated_cost ?? 0}
                  </p>
                  <p className="text-sm text-gray-600">
                    🌤 {day.weather?.temp ?? "--"}°C, {day.weather?.desc ?? "No data"}
                  </p>
                </div>
              </div>

              {/* Activities */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-yellow-50 to-orange-50 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <h4 className="font-semibold text-orange-700 flex items-center gap-2 mb-2">
                    <span className="text-xl">🌅</span> Morning
                  </h4>
                  <p className="text-gray-800 text-sm">
                    {day.morning?.name || String(day.morning)}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <h4 className="font-semibold text-indigo-700 flex items-center gap-2 mb-2">
                    <span className="text-xl">🌇</span> Afternoon
                  </h4>
                  <p className="text-gray-800 text-sm">
                    {day.afternoon?.name || String(day.afternoon)}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
                  <h4 className="font-semibold text-pink-700 flex items-center gap-2 mb-2">
                    <span className="text-xl">🌃</span> Evening
                  </h4>
                  <p className="text-gray-800 text-sm">
                    {day.evening?.name || String(day.evening)}
                  </p>
                </div>
              </div>

              {/* Selected Indicator */}
              {isSelected && (
                <div className="absolute top-2 right-2 text-blue-500 animate-bounce">
                  <span className="text-xl">✨</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Timeline;
