import React from "react";
import { Activity } from "../../api/types";

interface ActivityCardProps {
  activity: Activity;
  index: number;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({ activity, index }) => {
  const timeslotColors = {
    morning: "from-yellow-50 to-orange-100 border-orange-200 text-orange-800",
    afternoon: "from-blue-50 to-indigo-100 border-indigo-200 text-indigo-800",
    evening: "from-purple-50 to-pink-100 border-pink-200 text-pink-800",
    lunch: "from-green-50 to-emerald-100 border-emerald-200 text-emerald-800"
  };

  const slotColor = timeslotColors[activity.timeslot as keyof typeof timeslotColors] || timeslotColors.morning;

  return (
    <div className={`p-5 rounded-2xl border bg-gradient-to-br ${slotColor} shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between space-y-3`}>
      <div>
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-white/60">
            {activity.timeslot || `Slot ${index + 1}`}
          </span>
          <span className="text-xs font-medium bg-white/40 px-2 py-0.5 rounded-full">
            ⏳ {activity.estimateddurationminutes || 90} mins
          </span>
        </div>
        <h4 className="text-lg font-bold text-gray-800">{activity.name}</h4>
        {activity.description && <p className="text-sm text-gray-600 mt-1">{activity.description}</p>}
      </div>
      
      <div className="flex justify-between items-center text-xs pt-2 border-t border-black/5">
        <span className="font-semibold text-gray-800">
          💰 {activity.estimatedcost ? `${activity.currency || "$"} ${activity.estimatedcost}` : "Free"}
        </span>
        {activity.traveltonext && activity.traveltonext.distancekm > 0 && (
          <span className="text-gray-500 italic">
            🚶 {activity.traveltonext.distancekm} km to next
          </span>
        )}
      </div>
    </div>
  );
};
