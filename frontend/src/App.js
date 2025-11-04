import React from 'react';
import Dashboard from './pages/Dashboard';

function App() {
  // Pretend itinerary data (replace with real from backend later)
  const mockItinerary = {
    destination: 'Paris',
    activities: [{ name: 'Eiffel Tower', lat: 48.8584, lon: 2.2945 }],
    days: [{ morning: 'Breakfast', afternoon: 'Museum', evening: 'Dinner' }],
    costs: { food: 200, hotel: 500 },
  };

  return <Dashboard itinerary={mockItinerary} />;
}

export default App;