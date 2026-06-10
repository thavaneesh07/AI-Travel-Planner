import React from "react";
import { Trip } from "../../api/types";
import { BudgetSummary } from "./BudgetSummary";

const getFlagEmoji = (countryName: string) => {
  const mapping: { [key: string]: string } = {
    india: "🇮🇳",
    france: "🇫🇷",
    japan: "🇯🇵",
    "united kingdom": "🇬🇧",
    uk: "🇬🇧",
    "united states": "🇺🇸",
    usa: "🇺🇸",
    us: "🇺🇸",
    italy: "🇮🇹",
    spain: "🇪🇸",
    switzerland: "🇨🇭",
    australia: "🇦🇺",
    indonesia: "🇮🇩",
    thailand: "🇹🇭",
    singapore: "🇸🇬",
  };
  return mapping[countryName.toLowerCase().trim()] || "🏳️";
};

const GUIDE_DATA: {
  [key: string]: {
    customs: string;
    safety: string;
    visa: string;
    transport: string;
  };
} = {
  india: {
    customs: "Respect local traditions by removing shoes at temples. Tipping around 10% is customary in sit-down restaurants.",
    safety: "Drink only bottled/purified water. Keep a note of local emergency numbers (112).",
    visa: "Most travelers require an e-Tourist Visa (e-TV) before arrival. Passport must be valid for at least 6 months.",
    transport: "Use pre-paid taxis or ride-hailing apps like Uber or Ola. Auto-rickshaws are great for short city rides."
  },
  france: {
    customs: "Always greet with 'Bonjour' or 'Bonsoir'. Tipping is not required (service charge included), but rounding up is appreciated.",
    safety: "Be alert for pickpockets in tourist hotspots, train stations, and metro corridors.",
    visa: "Schengen rules apply. Citizens from US, UK, Canada, Australia can visit visa-free for up to 90 days.",
    transport: "Metro and RER train lines are highly efficient in cities. High-speed TGV connects major regions."
  },
  japan: {
    customs: "Bow slightly to greet. Tipping is considered offensive; good service is standard. Avoid eating or drinking while walking.",
    safety: "Very high safety standards. Tap water is safe. Keep an eye out for earthquake evacuation signs.",
    visa: "Visa waiver agreement applies to many countries for up to 90 days. Check official rules before flight.",
    transport: "Incredibly punctual trains and Shinkansen (bullet trains). Get a Suica/Pasmo card for easy bus and local subway travel."
  }
};

const CountryGuide: React.FC<{ country: string }> = ({ country }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const countryKey = country.toLowerCase().trim();
  const flag = getFlagEmoji(country);
  const data = GUIDE_DATA[countryKey] || {
    customs: "Respect local dress codes and cultural norms. Research customs and tipping traditions.",
    safety: "Keep valuables secure. Always have local emergency numbers and travel insurance details handy.",
    visa: "Ensure passport has at least 6 months validity. Verify entry visa requirements before booking travel.",
    transport: "Prefer registered taxis or official ride-sharing apps. Learn local driving rules and public transport layouts."
  };

  return (
    <div className="bg-white border border-gray-150 rounded-3xl shadow-sm overflow-hidden transition-all duration-300">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 text-left font-bold text-gray-800 hover:bg-gray-50/50 transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{flag}</span>
          <div>
            <h4 className="text-base font-extrabold text-gray-800">Essential Guide to {country}</h4>
            <p className="text-xs text-gray-400 font-semibold mt-0.5">Visa, safety, transport, and etiquette</p>
          </div>
        </div>
        <span className="text-gray-400 transition-transform duration-200 text-xs" style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0deg)" }}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div className="p-6 border-t border-gray-100 bg-gradient-to-b from-white to-gray-50/30 grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
          <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100/80 shadow-sm">
            <h5 className="font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
              <span>🤝</span> Customs & Etiquette
            </h5>
            <p className="text-gray-600 font-medium leading-relaxed pt-1">{data.customs}</p>
          </div>

          <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100/80 shadow-sm">
            <h5 className="font-extrabold text-red-900 uppercase tracking-wider flex items-center gap-1.5">
              <span>🛡️</span> Safety & Health
            </h5>
            <p className="text-gray-600 font-medium leading-relaxed pt-1">{data.safety}</p>
          </div>

          <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100/80 shadow-sm">
            <h5 className="font-extrabold text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
              <span>🛂</span> Visa & Entry
            </h5>
            <p className="text-gray-600 font-medium leading-relaxed pt-1">{data.visa}</p>
          </div>

          <div className="space-y-1 bg-white p-4 rounded-2xl border border-gray-100/80 shadow-sm">
            <h5 className="font-extrabold text-amber-950 uppercase tracking-wider flex items-center gap-1.5">
              <span>🚗</span> Transportation Tips
            </h5>
            <p className="text-gray-600 font-medium leading-relaxed pt-1">{data.transport}</p>
          </div>
        </div>
      )}
    </div>
  );
};

interface ItineraryViewProps {
  trip: Trip;
  selectedDay: number | null;
  onSelectDay: (day: number | null) => void;
}

export const ItineraryView: React.FC<ItineraryViewProps> = ({ trip, selectedDay, onSelectDay }) => {
  const totalCost = trip.days.reduce((acc, d) => acc + d.estimatedcost, 0);
  const budgetLimit = trip.budget?.dailybudget ? trip.budget.dailybudget * trip.days.length : 1000;

  const activeDayNumber = selectedDay || 1;
  const activeDay = trip.days.find((d) => d.day === activeDayNumber) || trip.days[0];

  return (
    <div className="space-y-6 animate-slide-up">
      {/* General Trip Info */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-3xl border border-gray-100 shadow-sm">
        <h2 className="text-3xl font-extrabold text-gray-800 mb-3">
          🌸 Trip to {trip.destination}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-600 font-medium">
          <div>📍 <b>Country:</b> {trip.country || "N/A"}</div>
          <div>🗓️ <b>Dates:</b> {trip.startdate} to {trip.enddate}</div>
          <div>🧍 <b>Travelers:</b> {trip.travelercount} ({trip.travelertype})</div>
          <div>🎨 <b>Interests:</b> {trip.interests.join(", ")}</div>
        </div>
      </div>

      {/* Budget Summary Card */}
      {trip.budget && (
        <BudgetSummary
          budget={trip.budget}
          totalLimit={budgetLimit}
          totalCost={totalCost}
          currency={trip.budget.currency || trip.days[0]?.activities[0]?.currency || "USD"}
        />
      )}

      {/* Country Guide */}
      {trip.country && (
        <CountryGuide country={trip.country} />
      )}

      {/* Horizontal Day Tabs Selector */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-200">
        {trip.days.map((day) => {
          const isActive = day.day === activeDayNumber;
          return (
            <button
              key={day.day}
              onClick={() => onSelectDay(day.day)}
              className={`px-5 py-3.5 rounded-2xl font-bold transition-all whitespace-nowrap shadow-sm border shrink-0 text-sm flex flex-col items-center justify-center min-w-[100px] cursor-pointer ${
                isActive
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white border-transparent"
                  : "bg-white hover:bg-gray-50 text-gray-700 border-gray-150"
              }`}
            >
              <span>Day {day.day}</span>
              {day.weather && (
                <span className={`text-[10px] font-semibold mt-0.5 ${isActive ? "text-white/80" : "text-gray-400"}`}>
                  🌤️ {Math.round(day.weather.temphighc || day.weather.temp || 0)}°C
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Selected Day Header */}
      {activeDay && (
        <div className="bg-white p-5 rounded-3xl border border-gray-100 shadow-sm space-y-3">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-extrabold text-xl text-gray-800 capitalize">
                {activeDay.theme || `Day ${activeDay.day} - Exploration`}
              </h3>
              <p className="text-xs text-gray-400 font-semibold mt-1">🗓️ Date: {activeDay.date}</p>
            </div>
            <div className="text-right">
              <span className="text-xl font-extrabold text-green-600">
                {trip.budget?.currency || "$"}{new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(activeDay.estimatedcost)}
              </span>
              <p className="text-[10px] text-gray-400 font-bold tracking-wider uppercase mt-0.5">Est. Cost</p>
            </div>
          </div>

          {activeDay.weather && (
            <div className="flex items-center gap-3 bg-blue-50/60 p-3 rounded-2xl border border-blue-100 text-blue-800 text-xs">
              <span className="text-lg">🌤️</span>
              <div>
                <span className="font-extrabold capitalize">{activeDay.weather.condition}</span>
                <span className="mx-2 text-blue-300">|</span>
                <span>Range: {activeDay.weather.templowc}°C - {activeDay.weather.temphighc}°C</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Step-by-Step Activities Vertical Timeline */}
      {activeDay && activeDay.activities && activeDay.activities.length > 0 ? (
        <div className="relative pl-8 space-y-6">
          <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-gradient-to-b from-blue-300 to-purple-300 rounded-full"></div>

          {activeDay.activities.map((act, idx) => {
            const timeslotColors = {
              morning: "bg-orange-50 text-orange-700 border-orange-200",
              afternoon: "bg-blue-50 text-blue-700 border-blue-200",
              evening: "bg-purple-50 text-purple-700 border-purple-200",
              lunch: "bg-green-50 text-green-700 border-green-200"
            };
            const slot = (act.timeslot || "").toLowerCase();
            const badgeStyle = timeslotColors[slot as keyof typeof timeslotColors] || timeslotColors.morning;

            return (
              <div key={idx} className="relative group">
                {/* Connected step dot */}
                <div className="absolute -left-[37px] top-1.5 flex items-center justify-center bg-blue-600 border-4 border-white text-white font-extrabold text-xs rounded-full w-7 h-7 shadow-md group-hover:scale-110 transition-all">
                  {idx + 1}
                </div>

                {/* Activity Card */}
                <div className="bg-white p-5 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md hover:border-blue-100 transition-all duration-300 space-y-2.5">
                  <div className="flex justify-between items-center">
                    <span className={`text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${badgeStyle}`}>
                      {act.timeslot || `Activity ${idx + 1}`}
                    </span>
                    <div className="flex gap-2 text-[11px] text-gray-500 font-semibold">
                      {act.estimateddurationminutes && (
                        <span>⏳ {act.estimateddurationminutes} mins</span>
                      )}
                      <span>💰 {act.estimatedcost ? `${trip.budget?.currency || "$"} ${new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(act.estimatedcost)}` : "Free"}</span>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-base font-extrabold text-gray-800 group-hover:text-blue-600 transition-colors">
                      {act.name}
                    </h4>
                    {act.description && (
                      <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                        {act.description}
                      </p>
                    )}
                  </div>

                  {act.traveltonext && act.traveltonext.distancekm > 0 && (
                    <div className="flex items-center gap-1.5 text-[11px] text-gray-400 font-medium pt-2 border-t border-gray-50">
                      <span>🚗</span>
                      <span>
                        {act.traveltonext.mode === "walk" ? "Walk" : "Drive"} {act.traveltonext.distancekm} km to next stop ({act.traveltonext.durationminutes} mins)
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white p-6 rounded-3xl border border-gray-100 text-center text-gray-500 text-sm">
          No activities planned for this day yet.
        </div>
      )}

      {/* Stepper Navigation Buttons */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-100">
        <button
          disabled={activeDayNumber <= 1}
          onClick={() => onSelectDay(activeDayNumber - 1)}
          className="px-4 py-2.5 rounded-xl bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-bold transition-all disabled:opacity-50 disabled:pointer-events-none text-xs flex items-center gap-1.5 shadow-sm cursor-pointer"
        >
          ← Prev Day
        </button>
        <span className="text-xs font-extrabold text-gray-500">
          Day {activeDayNumber} of {trip.days.length}
        </span>
        <button
          disabled={activeDayNumber >= trip.days.length}
          onClick={() => onSelectDay(activeDayNumber + 1)}
          className="px-4 py-2.5 rounded-xl bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-bold transition-all disabled:opacity-50 disabled:pointer-events-none text-xs flex items-center gap-1.5 shadow-sm cursor-pointer"
        >
          Next Day →
        </button>
      </div>
    </div>
  );
};
