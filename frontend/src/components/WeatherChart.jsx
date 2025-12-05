// src/components/WeatherChart.jsx
import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Area, AreaChart } from "recharts";

function WeatherChart({ days }) {
  if (!days || days.length === 0) return null;

  // Prepare data for Recharts
  const chartData = days.map((day) => ({
    date: day.date,
    temp: day.weather?.temp || 0,
    desc: day.weather?.desc || "N/A",
    icon: day.weather?.icon || "☀️", // Assuming an icon is available, or default to sun
  }));

  // Custom Tooltip Component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200 animate-fade-in">
          <p className="font-semibold text-gray-800">{`Date: ${label}`}</p>
          <p className="text-blue-600">{`Temperature: ${payload[0].value}°C`}</p>
          <p className="text-gray-600 flex items-center gap-2">
            <span className="text-2xl">{data.icon}</span>
            {data.desc}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-blue-200">
      <div className="mb-4 text-center">
        <h3 className="text-xl font-bold text-blue-700">Temperature Forecast</h3>
        <p className="text-sm text-gray-600">Hover over points for details</p>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12, fill: '#6b7280' }} 
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            domain={["auto", "auto"]} 
            tick={{ fontSize: 12, fill: '#6b7280' }}
            axisLine={{ stroke: '#d1d5db' }}
            label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area 
            type="monotone" 
            dataKey="temp" 
            stroke="#3b82f6" 
            strokeWidth={3} 
            fill="url(#tempGradient)" 
            activeDot={{ r: 8, fill: '#1e40af', stroke: '#fff', strokeWidth: 2 }}
            animationDuration={1500}
            animationEasing="ease-in-out"
          />
        </AreaChart>
      </ResponsiveContainer>
      <div className="mt-4 text-center text-sm text-gray-500">
        Data sourced from weather API
      </div>
    </div>
  );
}

export default WeatherChart;
