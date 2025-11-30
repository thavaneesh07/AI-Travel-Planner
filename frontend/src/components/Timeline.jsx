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
    <div className="flex flex-col gap-4">
      {localDays.map((day, i) => {
        const dateString = day.date || getDateForDay(i);

        return (
          <div
            key={day.day}
            onClick={() => onDaySelect(day.day)}
            className={`cursor-pointer p-4 border rounded-xl shadow-sm transition-all duration-300 ${
              selectedDay === day.day
                ? "bg-blue-100 border-blue-400"
                : "bg-white hover:bg-gray-50"
            }`}
          >
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-blue-700 text-lg">
                Day {day.day} — {dateString}
              </h3>
              <p className="text-gray-600 text-sm">
                💸 ${day.estimated_cost ?? 0}
              </p>
            </div>

            <p className="text-sm text-gray-700 mt-1">
              🌤 {day.weather?.temp ?? "--"}°C, {day.weather?.desc ?? "No data"}
            </p>

            <ul className="mt-2 space-y-1 text-gray-800">
              <li>
                🌅 <strong>Morning:</strong>{" "}
                {day.morning?.name || String(day.morning)}
              </li>
              <li>
                🌇 <strong>Afternoon:</strong>{" "}
                {day.afternoon?.name || String(day.afternoon)}
              </li>
              <li>
                🌃 <strong>Evening:</strong>{" "}
                {day.evening?.name || String(day.evening)}
              </li>
            </ul>
          </div>
        );
      })}
    </div>
  );
}

export default Timeline;
