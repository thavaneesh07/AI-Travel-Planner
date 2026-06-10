import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

interface RouteMapProps {
  destination: string;
  activities: any[];
  routeGeometry?: any;
}

function ChangeMapView({ center, activities }: { center: [number, number]; activities: any[] }) {
  const map = useMap();
  useEffect(() => {
    if (activities && activities.length > 0 && map) {
      const coords = activities
        .map(act => act.coordinates ? [act.coordinates.lat, act.coordinates.lng] as [number, number] : null)
        .filter(Boolean) as [number, number][];
      if (coords.length > 0) {
        map.fitBounds(coords, { padding: [50, 50] });
        return;
      }
    }
    if (center && map) {
      map.setView(center, 12);
    }
  }, [center, activities, map]);
  return null;
}

export const RouteMap: React.FC<RouteMapProps> = ({ destination, activities, routeGeometry }) => {
  const [center, setCenter] = useState<[number, number]>([48.8566, 2.3522]);
  
  useEffect(() => {
    if (!destination) return;
    const fetchCoords = async () => {
      try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(destination)}`);
        const data = await res.json();
        if (data && data.length > 0) {
          setCenter([parseFloat(data[0].lat), parseFloat(data[0].lon)]);
        }
      } catch (err) {
        console.error("Geocoding map center failed:", err);
      }
    };
    fetchCoords();
  }, [destination]);

  const polylineCoords = routeGeometry || activities
    .map(act => act.coordinates ? [act.coordinates.lat, act.coordinates.lng] : null)
    .filter(Boolean);

  return (
    <div className="w-full h-[400px] rounded-3xl overflow-hidden shadow-lg border border-gray-100 relative z-0">
      <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
        <ChangeMapView center={center} activities={activities} />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='© OpenStreetMap contributors'
        />
        
        {activities.map((act, idx) => {
          if (!act.coordinates) return null;
          const pos: [number, number] = [act.coordinates.lat, act.coordinates.lng];
          
          return (
            <Marker
              key={idx}
              position={pos}
              icon={L.divIcon({
                html: `<div class="flex items-center justify-center bg-blue-600 border-2 border-white text-white font-bold text-xs rounded-full w-6 h-6 shadow-md">${idx + 1}</div>`,
                className: "",
                iconSize: [24, 24],
                iconAnchor: [12, 12]
              })}
            >
              <Popup>
                <div className="p-1">
                  <h4 className="font-bold text-blue-700">{act.name}</h4>
                  <p className="text-xs text-gray-500 capitalize">{act.category}</p>
                  {act.description && <p className="text-xs mt-1">{act.description}</p>}
                </div>
              </Popup>
            </Marker>
          );
        })}

        {polylineCoords.length > 1 && (
          <Polyline
            positions={polylineCoords}
            color="#3b82f6"
            weight={4}
            opacity={0.8}
            dashArray="5, 10"
          />
        )}
      </MapContainer>
    </div>
  );
};
