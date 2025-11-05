import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; // Makes the map look good

function MapView({ activities }) { // activities is a list of places from the trip
  return (
    <div style={{ height: '400px', width: '100%' }}>
      <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: '100%' }}> {/* Default to London */}
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {activities?.map((activity, index) => (
          <Marker key={index} position={[activity.lat, activity.lon]}>
            <Popup>{activity.name}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapView;