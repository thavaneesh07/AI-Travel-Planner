// src/components/MapView.jsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useMap } from "react-leaflet";
import L from "leaflet";

function ChangeView({ center }) {
  const map = useMap();
  map.setView(center);
  return null;
}
function FitBounds({ markers }) {
  const map = useMap();

  useEffect(() => {
    if (!markers || markers.length === 0) return;
    const bounds = L.latLngBounds(markers.map(m => [m.lat, m.lon]));
    map.fitBounds(bounds, { padding: [50, 50] });
  }, [markers, map]);

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

// 📍 Fetch real coordinates for activities
useEffect(() => {
  if (!activities || activities.length === 0) return;

  const fetchActivityCoords = async () => {
    const newMarkers = [];

    // 👇 Loop with index to assign type
    for (const [idx, act] of activities.entries()) {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(act + " in " + destination)}`
        );
        const data = await res.json();

        console.log("Geocoded result for", act, "=>", data);

        if (data.length > 0) {
          newMarkers.push({
            id: act,
            lat: parseFloat(data[0].lat),
            lon: parseFloat(data[0].lon),
            name: act,
            type: idx % 3 === 0 ? "morning" : idx % 3 === 1 ? "afternoon" : "evening",
          });
        } else {
          // fallback — slightly offset random position near center
          newMarkers.push({
            id: act + "-approx",
            lat: center[0] + Math.random() * 0.05 - 0.025,
            lon: center[1] + Math.random() * 0.05 - 0.025,
            name: act + " (approx.)",
            type: idx % 3 === 0 ? "morning" : idx % 3 === 1 ? "afternoon" : "evening",
          });
        }
      } catch (err) {
        console.error("Failed to fetch coords for", act, err);
      }
    }

    setMarkers(newMarkers);
  };

  fetchActivityCoords();
}, [activities, destination]);


  return (
  <div className="w-full h-[400px] mb-8 rounded-lg overflow-hidden shadow-md border border-gray-200">
    <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
      <ChangeView center={center} />  {/* 👈 Add this line */}
       <FitBounds markers={markers} />
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
      />
      {markers.map((m) => (
  <Marker
    key={m.id}
    position={[m.lat, m.lon]}
    icon={L.divIcon({
      className: "custom-marker",
      html: `<div style="
        background-color: ${
          m.type === "morning"
            ? "#facc15" // 🟡 yellow
            : m.type === "afternoon"
            ? "#3b82f6" // 🔵 blue
            : "#f87171" // 🔴 red (evening)
        };
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 0 3px rgba(0,0,0,0.4);
      "></div>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
      popupAnchor: [0, -8],
    })}
  >
    <Popup>
      <strong>{m.name}</strong> <br />
      ({m.type})
    </Popup>
  </Marker>
))}

    </MapContainer>
  </div>
);

}

export default MapView;
