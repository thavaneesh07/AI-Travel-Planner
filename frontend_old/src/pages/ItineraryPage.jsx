import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ItineraryPage() {
  const [itinerary, setItinerary] = useState(null); // Holds the trip plan

  useEffect(() => {
    // When the page loads, ask the backend for a trip plan
    const fetchItinerary = async () => {
      try {
        const result = await axios.get('http://localhost:8000/api/itineraries/1'); // Get trip ID 1 (pretend data)
        setItinerary(result.data);
      } catch (error) {
        console.error('Oops, error:', error);
      }
    };
    fetchItinerary();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Your Trip Plan</h1>
      {itinerary ? (
        <div>
          <h2>{itinerary.destination}</h2>
          <p>From {itinerary.start_date} to {itinerary.end_date}</p>
          <p>Budget: ${itinerary.budget}</p>
          {/* For now, just show a simple card. Later we'll make it fancier. */}
          <div style={{ border: '1px solid gray', padding: '10px', margin: '10px 0' }}>
            <h3>Day 1</h3>
            <p>Morning: Eat breakfast. Afternoon: Visit museum. Evening: Dinner.</p>
          </div>
        </div>
      ) : (
        <p>Loading trip...</p>
      )}
    </div>
  );
}

export default ItineraryPage;