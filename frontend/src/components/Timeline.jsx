// src/components/Timeline.jsx
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

function Timeline({ days }) {
  const [expandedDay, setExpandedDay] = useState(null);

  if (!days || days.length === 0) return null;

  const toggleDay = (dayNumber) => {
    setExpandedDay(expandedDay === dayNumber ? null : dayNumber);
  };

  return (
    <div className="w-full mb-10">
      <h3 className="text-2xl font-bold text-indigo-700 mb-6 flex items-center gap-2">
        🕓 Trip Timeline
      </h3>

      <div className="flex flex-col gap-4">
        {days.map((day) => (
          <motion.div
            key={day.day}
            layout
            className={`border-l-4 pl-4 py-3 rounded-lg cursor-pointer ${
              expandedDay === day.day ? "bg-indigo-50 border-indigo-600" : "border-indigo-300 bg-white"
            } hover:bg-indigo-100 transition`}
            onClick={() => toggleDay(day.day)}
          >
            <div className="flex justify-between items-center">
              <p className="font-semibold text-lg text-gray-800">
                Day {day.day} — {day.date}
              </p>
              <span className="text-sm text-gray-500">
                {expandedDay === day.day ? "▲ Collapse" : "▼ Expand"}
              </span>
            </div>

            <AnimatePresence>
              {expandedDay === day.day && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mt-3 text-gray-700 space-y-2"
                >
                  <p>
                    🌤 <strong>Weather:</strong> {day.weather?.temp}°C, {day.weather?.desc}
                  </p>
                  <p>🌅 <strong>Morning:</strong> {day.morning}</p>
                  <p>🌇 <strong>Afternoon:</strong> {day.afternoon}</p>
                  <p>🌃 <strong>Evening:</strong> {day.evening}</p>
                  <p className="font-semibold text-green-700">
                    💸 Cost: ${day.estimated_cost}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default Timeline;
