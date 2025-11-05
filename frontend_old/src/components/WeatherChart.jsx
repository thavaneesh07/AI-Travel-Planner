import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function WeatherChart({ destination }) {
  const [weather, setWeather] = useState([]);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const result = await axios.get(`http://localhost:8000/api/weather?location=${destination}`);
        setWeather(result.data.forecast); // Pretend forecast data
      } catch (error) {
        console.error('Oops, error:', error);
      }
    };
    if (destination) fetchWeather();
  }, [destination]);

  return (
    <div>
      <h2>Weather Forecast</h2>
      <LineChart width={400} height={300} data={weather}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="temp" stroke="#8884d8" />
      </LineChart>
    </div>
  );
}

export default WeatherChart;