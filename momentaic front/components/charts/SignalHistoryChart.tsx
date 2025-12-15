import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { SignalScores } from '../../types';
import { formatDate } from '../../lib/utils';

interface SignalHistoryChartProps {
  data: SignalScores[];
}

export function SignalHistoryChart({ data }: SignalHistoryChartProps) {
  // Defensive check: if data is not an array, render nothing or placeholder
  if (!Array.isArray(data)) {
    return <div className="h-[300px] w-full flex items-center justify-center text-gray-400 text-sm">No history data available</div>;
  }

  const chartData = [...data].reverse().map(item => ({
    ...item,
    formattedDate: formatDate(item.calculated_at),
  }));

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 10,
            left: -20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
          <XAxis 
            dataKey="formattedDate" 
            tick={{fontSize: 12, fill: '#6b7280'}} 
            tickLine={false}
            axisLine={{stroke: '#e5e7eb'}}
          />
          <YAxis 
            domain={[0, 100]} 
            tick={{fontSize: 12, fill: '#6b7280'}} 
            tickLine={false}
            axisLine={false}
          />
          <Tooltip 
            contentStyle={{borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="composite_score"
            name="Composite"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="technical_velocity_score"
            name="Tech Velocity"
            stroke="#10b981" // green
            strokeWidth={1.5}
            strokeDasharray="5 5"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="pmf_score"
            name="PMF"
            stroke="#f59e0b" // yellow
            strokeWidth={1.5}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}