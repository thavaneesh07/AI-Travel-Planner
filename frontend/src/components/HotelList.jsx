import React from "react";

function HotelList({ hotels = [] }) {
  if (!hotels || hotels.length === 0) {
    return <p className="text-gray-500">No hotels found.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {hotels.map((hotel, idx) => (
        <div
          key={idx}
          className="p-4 border rounded-xl shadow-sm bg-white hover:shadow-md transition-all"
        >
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-blue-700">
              {hotel.name}
            </h2>

            {/* Score badge */}
            <span className="px-3 py-1 bg-green-100 text-green-700 font-semibold rounded-lg">
              {hotel.score}/100
            </span>
          </div>

          <p className="text-gray-600 text-sm">
            ⭐ {hotel.rating} | 💰 ${hotel.price_per_night}/night
          </p>

          <p className="text-sm mt-1 text-gray-700">📍 {hotel.address}</p>

          <p className="text-sm mt-2 italic text-gray-600">
            {hotel.reason}
          </p>
        </div>
      ))}
    </div>
  );
}

export default HotelList;
