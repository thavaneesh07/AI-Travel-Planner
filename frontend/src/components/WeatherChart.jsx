// src/components/WeatherChart.jsx
import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

function WeatherChart({ days }) {
  if (!days || days.length === 0) return null;

  // Prepare data for Recharts
  const chartData = days.map((day) => ({
    date: day.date,
    temp: day.weather?.temp || 0,
    desc: day.weather?.desc || "N/A",
  }));

  return (
    <div className="bg-white p-6 rounded-2xl shadow-md mt-8">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ccc" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip formatter={(value) => `${value}°C`} labelFormatter={(date) => `Date: ${date}`} />
          <Line type="monotone" dataKey="temp" stroke="#3b82f6" strokeWidth={3} activeDot={{ r: 6 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default WeatherChart;
