// src/components/MapView.jsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useMap } from "react-leaflet";

function ChangeView({ center }) {
  const map = useMap();
  map.setView(center);
  return null;
}


function MapView({ activities = [], destination }) {
  const [center, setCenter] = useState([48.8566, 2.3522]); // Default: Paris
  const [markers, setMarkers] = useState([]);

  // 🗺️ Fetch destination coordinates
  useEffect(() => {
    if (!destination) return;

    const fetchCoords = async () => {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(destination)}`
    );
    const data = await res.json();

    console.log("Geocoding results:", data); // 👈 Add this line to debug API response

    if (data.length > 0) {
      const lat = parseFloat(data[0].lat);
      const lon = parseFloat(data[0].lon);
      setCenter([lat, lon]);
    } else {
      console.warn("No geocoding results for:", destination);
    }
  } catch (err) {
    console.error("Geocoding failed:", err);
  }
};


    fetchCoords();
  }, [destination]);

  // 📍 Create fake markers for daily activities (just spread around city center)
  useEffect(() => {
    if (!activities || activities.length === 0) return;

    const newMarkers = activities.map((act, idx) => ({
      id: idx,
      lat: center[0] + Math.random() * 0.05 - 0.025,
      lon: center[1] + Math.random() * 0.05 - 0.025,
      name: act,
    }));

    setMarkers(newMarkers);
  }, [activities, center]);

  return (
  <div className="w-full h-[400px] mb-8 rounded-lg overflow-hidden shadow-md border border-gray-200">
    <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
      <ChangeView center={center} />  {/* 👈 Add this line */}
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
      />
      {markers.map((m) => (
        <Marker key={m.id} position={[m.lat, m.lon]}>
          <Popup>{m.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  </div>
);

}

export default MapView;
