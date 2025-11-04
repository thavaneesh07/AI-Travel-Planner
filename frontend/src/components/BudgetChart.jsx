import React from 'react';
import { PieChart, Pie, Cell } from 'recharts';

function BudgetChart({ costs }) { // costs is like {food: 200, hotel: 500}
  const data = Object.entries(costs).map(([key, value]) => ({ name: key, value }));
  const colors = ['#8884d8', '#82ca9d', '#ffc658'];

  return (
    <div>
      <h2>Budget Breakdown</h2>
      <PieChart width={400} height={400}>
        <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
          {data.map((entry, index) => <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />)}
        </Pie>
      </PieChart>
    </div>
  );
}

export default BudgetChart;