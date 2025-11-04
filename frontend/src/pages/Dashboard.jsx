import React from 'react';
import MapView from '../components/MapView';
import Timeline from '../components/Timeline';
import BudgetChart from '../components/BudgetChart';
import WeatherChart from '../components/WeatherChart';

function Dashboard({ itinerary }) {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Trip Dashboard</h1>
      <MapView activities={itinerary.activities} />
      <Timeline itinerary={itinerary} />
      <BudgetChart costs={itinerary.costs} />
      <WeatherChart destination={itinerary.destination} />
    </div>
  );
}

export default Dashboard;