// src/components/MapView.jsx
import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

/* Helper for smooth view */
function ChangeView({ center }) {
  const map = useMap();
  if (center && map) {
    try {
      map.setView(center, 12);
    } catch {}
  }
  return null;
}

/* Auto-fit all markers */
function FitBounds({ markers }) {
  const map = useMap();
  useEffect(() => {
    if (!map || markers.length === 0) return;
    try {
      const bounds = L.latLngBounds(markers.map(m => [m.lat, m.lon]));
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [50, 50] });
    } catch {}
  }, [markers, map]);
  return null;
}

function MapView({ activities = [], destination, hotels = [] }) {
  const [center, setCenter] = useState([48.8566, 2.3522]);
  const [markers, setMarkers] = useState([]);
  const mapRef = useRef(null);

  const [mapKey, setMapKey] = useState(() => `map-${Date.now()}`);

  /* Reset map when destination changes */
  useEffect(() => {
    setMarkers([]);
    setMapKey(`map-${destination}-${Date.now()}`);
  }, [destination]);

  /* Fetch destination geocode ONLY ONCE */
  useEffect(() => {
    if (!destination) return;

    let cancelled = false;
    const fetchCoords = async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
            destination
          )}`
        );
        const data = await res.json();
        if (cancelled) return;

        if (data && data.length > 0) {
          const lat = parseFloat(data[0].lat);
          const lon = parseFloat(data[0].lon);
          setCenter([lat, lon]);
        }
      } catch (err) {
        console.error("Geocode failed:", err);
      }
    };

    fetchCoords();
    return () => (cancelled = true);
  }, [destination]);

  /* ACTIVITIES → markers */
  useEffect(() => {
    if (!activities || activities.length === 0) {
      setMarkers([]);
      return;
    }

    let cancelled = false;

    const fetchActivityCoords = async () => {
      const promises = activities.map(async (act, idx) => {
        // 🔥 New: If backend already provided lat/lon → use directly
        if (act.lat && act.lon) {
          return {
            id: `${idx}-${act.name}`,
            lat: act.lat,
            lon: act.lon,
            name: act.name,
            type: act.type || "activity",
          };
        }

        // Otherwise → geocode fallback
        try {
          const q = `${act.name} in ${destination}`;
          const res = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
              q
            )}`
          );
          const data = await res.json();

          if (cancelled) return null;

          if (data && data.length > 0) {
            return {
              id: `${idx}-${act.name}`,
              lat: parseFloat(data[0].lat),
              lon: parseFloat(data[0].lon),
              name: act.name,
              type: act.type || "activity",
            };
          }
        } catch {}

        // Final fallback → random small offset near center
        return {
          id: `${idx}-${act.name}-approx`,
          lat: center[0] + (Math.random() * 0.02 - 0.01),
          lon: center[1] + (Math.random() * 0.02 - 0.01),
          name: act.name + " (approx.)",
          type: act.type || "activity",
        };
      });

      const results = await Promise.all(promises);
      if (!cancelled) {
        setMarkers(results.filter(m => m !== null));
      }
    };

    fetchActivityCoords();
    return () => (cancelled = true);
  }, [activities, destination, center]);

  return (
    <div className="w-full h-[400px] mb-8 rounded-lg overflow-hidden shadow-md border border-gray-200">
      <MapContainer
        key={mapKey}
        center={center}
        zoom={12}
        style={{ height: "100%", width: "100%" }}
        whenCreated={(mapInstance) => (mapRef.current = mapInstance)}
      >
        <ChangeView center={center} />
        <FitBounds markers={markers} />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='© OpenStreetMap contributors'
        />

        {/* Activity markers */}
        {markers.map((m) => (
          <Marker
            key={m.id}
            position={[m.lat, m.lon]}
            icon={L.divIcon({
              html: `<div style="
                background-color: ${
                  m.type === "morning"
                    ? "#facc15"
                    : m.type === "afternoon"
                    ? "#3b82f6"
                    : "#f87171"
                };
                width: 14px; height: 14px; border-radius: 50%;
                border: 2px solid white; box-shadow: 0 0 3px rgba(0,0,0,0.4);
              "></div>`,
              iconSize: [14, 14],
              iconAnchor: [7, 7],
            })}
          >
            <Popup>
              <strong>{m.name}</strong>
              <br />
              ({m.type})
            </Popup>
          </Marker>
        ))}

        {/* Hotel markers */}
        {hotels.map((hotel, idx) => (
          <Marker
            key={`hotel-${idx}`}
            position={[hotel.latitude, hotel.longitude]}
            icon={new L.Icon({
              iconUrl:
                "https://cdn-icons-png.flaticon.com/512/139/139899.png?raw=1",
              iconSize: [32, 32],
              iconAnchor: [16, 32],
              popupAnchor: [0, -28],
            })}
          >
            <Popup>
              <strong>{hotel.name}</strong>
              <br />⭐ {hotel.rating}
              <br />💰 ${hotel.price_per_night}/night
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapView;
