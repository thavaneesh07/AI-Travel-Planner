// src/components/Timeline.jsx
import React from "react";

function Timeline({ days = [], onDaySelect, selectedDay }) {
  if (!days || days.length === 0) return null;

  return (
    <div className="mb-8">
      <h3 className="text-2xl font-bold text-indigo-700 mb-4 flex items-center gap-2">
        🕓 Travel Timeline
      </h3>
      <div className="flex overflow-x-auto gap-4 pb-2">
        {days.map((day) => (
          <div
            key={day.day}
            className={`flex-shrink-0 p-4 rounded-2xl border-2 min-w-[220px] cursor-pointer transition-all ${
              selectedDay === day.day
                ? "border-indigo-600 bg-indigo-50 shadow-md scale-105"
                : "border-gray-200 bg-white hover:shadow"
            }`}
            onClick={() => onDaySelect?.(day.day)}
          >
            <p className="text-lg font-semibold text-indigo-800">
              Day {day.day} — {day.date}
            </p>
            <p className="text-gray-700">
              ☀️ {day.weather?.temp}°C, {day.weather?.desc}
            </p>
            <p className="mt-1 text-gray-600">🌅 {day.morning}</p>
            <p className="text-gray-600">🌇 {day.afternoon}</p>
            <p className="text-gray-600">🌃 {day.evening}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Timeline;
