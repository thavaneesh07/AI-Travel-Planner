// src/components/BudgetChart.jsx
import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"];

function BudgetChart({ days }) {
  if (!days || days.length === 0) return null;

  const data = days.map((day) => ({
    name: `Day ${day.day}`,
    value: day.estimated_cost,
  }));

  return (
    <div className="mt-10 bg-white rounded-2xl p-6 shadow-md border border-gray-100">
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            label={({ name, value }) => `${name}: $${value}`}
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BudgetChart;
