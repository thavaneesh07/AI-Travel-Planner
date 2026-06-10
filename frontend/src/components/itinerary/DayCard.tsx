import React from "react";
import { TripDay } from "../../api/types";
import { ActivityCard } from "./ActivityCard";

interface DayCardProps {
  day: TripDay;
  isSelected: boolean;
  onClick: () => void;
}

export const DayCard: React.FC<DayCardProps> = ({ day, isSelected, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`relative cursor-pointer ml-12 p-6 bg-white rounded-3xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-100 transition-all duration-300 ${
        isSelected ? "ring-2 ring-blue-500 bg-gradient-to-r from-blue-50/50 to-indigo-50/50" : ""
      }`}
    >
      <div className="absolute -left-[54px] top-6 w-5 h-5 rounded-full border-4 border-white shadow-md bg-blue-500"></div>

      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-extrabold text-xl text-gray-800 flex items-center gap-2">
            Day {day.day} — {day.date}
          </h3>
          {day.theme && <p className="text-sm text-gray-500 italic mt-0.5">{day.theme}</p>}
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-green-600">${day.estimatedcost}</p>
          {day.weather && (
            <p className="text-xs text-gray-400">
              🌤 {day.weather.templowc}°C - {day.weather.temphighc}°C | {day.weather.condition}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {day.activities.map((act, idx) => (
          <ActivityCard key={idx} activity={act} index={idx} />
        ))}
      </div>
    </div>
  );
};
