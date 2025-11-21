// src/components/Timeline.jsx
import React from "react";

function Timeline({ days = [], selectedDay, onDaySelect }) {
  if (!days || days.length === 0) return null;

  const getDateForDay = (index) => {
    try {
      const start = new Date(days[0].date || days[0].start_date || days[0].iso_date);
      const result = new Date(start);
      result.setDate(start.getDate() + index);
      return result.toISOString().slice(0, 10);
    } catch {
      return "";
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {days.map((day, i) => {
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
