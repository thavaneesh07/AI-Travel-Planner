// src/components/MapView.jsx
import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

/* Small helper to set view (smoother) */
function ChangeView({ center }) {
  const map = useMap();
  if (!center || !map) return null;
  try {
    map.setView(center, 12);
  } catch (e) {
    // ignore if map not ready
  }
  return null;
}

/* Fit map to markers bounds */
function FitBounds({ markers }) {
  const map = useMap();
  useEffect(() => {
    if (!map || !markers || markers.length === 0) return;
    try {
      const bounds = L.latLngBounds(markers.map((m) => [m.lat, m.lon]));
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [50, 50] });
    } catch (e) {
      console.warn("FitBounds failed:", e);
    }
  }, [markers, map]);
  return null;
}

function MapView({ activities = [], destination }) {
  const [center, setCenter] = useState([48.8566, 2.3522]); // Paris default
  const [markers, setMarkers] = useState([]);
  const mapRef = useRef(null);

  // mapKey will force full remount of MapContainer when destination changes
  const [mapKey, setMapKey] = useState(() => `map-${Date.now()}`);

  useEffect(() => {
    // whenever destination changes, clear markers and bump mapKey to remount MapContainer
    setMarkers([]);
    setMapKey(`map-${destination || "default"}-${Date.now()}`);
    console.log("🗺️ mapKey updated:", destination, mapKey);
  }, [destination]);

  // 1) fetch destination center (geocode)
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
        console.log("Geocoding results for destination:", destination, data?.length);

        if (cancelled) return;

        if (data && data.length > 0) {
          const lat = parseFloat(data[0].lat);
          const lon = parseFloat(data[0].lon);
          setCenter([lat, lon]);

          // if map exists, set view (safe)
          if (mapRef.current && typeof mapRef.current.setView === "function") {
            try {
              mapRef.current.setView([lat, lon], 12);
            } catch (e) {
              /* ignore */
            }
          }
        } else {
          console.warn("No geocoding results for:", destination);
        }
      } catch (err) {
        console.error("Geocoding failed:", err);
      }
    };

    fetchCoords();
    return () => {
      cancelled = true;
    };
  }, [destination]);

  // 2) fetch activity coordinates (after center and destination available)
  useEffect(() => {
    if (!activities || activities.length === 0) {
      setMarkers([]);
      return;
    }
    if (!destination) return;

    let cancelled = false;
    const fetchActivityCoords = async () => {
      // Parallelize fetches using Promise.all for faster loading
      const promises = activities.map(async (act, idx) => {
        try {
          // add "in <destination>" to help geocoder find the correct city location
          const q = `${act} in ${destination}`;
          const res = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}`
          );
          const data = await res.json();

          if (cancelled) return null;

          if (data && data.length > 0) {
            return {
              id: `${idx}-${act}`,
              lat: parseFloat(data[0].lat),
              lon: parseFloat(data[0].lon),
              name: act,
              type: idx % 3 === 0 ? "morning" : idx % 3 === 1 ? "afternoon" : "evening",
            };
          } else {
            // fallback: small randomized offset near current center
            return {
              id: `${idx}-${act}-approx`,
              lat: center[0] + (Math.random() * 0.02 - 0.01),
              lon: center[1] + (Math.random() * 0.02 - 0.01),
              name: act + " (approx.)",
              type: idx % 3 === 0 ? "morning" : idx % 3 === 1 ? "afternoon" : "evening",
            };
          }
        } catch (err) {
          console.error("Failed to fetch coords for", act, err);
          return null;
        }
      });

      // Wait for all promises to resolve
      const results = await Promise.all(promises);
      // Filter out nulls (from errors or cancellations) and set markers
      if (!cancelled) {
        const newMarkers = results.filter(marker => marker !== null);
        setMarkers(newMarkers);
      }
    };

    // small delay to let center settle (helps ordering)
    const t = setTimeout(() => fetchActivityCoords(), 200);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [activities, destination, center]);

  // debug logs — remove later
  // console.log("Rendering Map for:", destination, "center:", center, "markers:", markers.length);

  return (
    <div className="w-full h-[400px] mb-8 rounded-lg overflow-hidden shadow-md border border-gray-200">
      <MapContainer
        key={mapKey} // force remount on destination change
        center={center}
        zoom={12}
        style={{ height: "100%", width: "100%" }}
        whenCreated={(mapInstance) => {
          mapRef.current = mapInstance;
        }}
      >
        <ChangeView center={center} />
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
                  m.type === "morning" ? "#facc15" : m.type === "afternoon" ? "#3b82f6" : "#f87171"
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
