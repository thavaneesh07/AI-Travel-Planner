import React from 'react';

function Timeline({ itinerary }) {
  return (
    <div>
      <h2>Day-by-Day Plan</h2>
      {itinerary.days?.map((day, index) => (
        <div key={index} style={{ border: '1px solid gray', padding: '10px', margin: '10px 0' }}>
          <h3>Day {index + 1}</h3>
          <p>Morning: {day.morning}</p>
          <p>Afternoon: {day.afternoon}</p>
          <p>Evening: {day.evening}</p>
        </div>
      ))}
    </div>
  );
}

export default Timeline;