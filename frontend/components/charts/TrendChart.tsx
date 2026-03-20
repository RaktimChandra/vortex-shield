'use client';

import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface TrendChartProps {
  data: any[];
  dataKey: string;
  xAxisKey: string;
  color?: string;
  type?: 'line' | 'area';
  height?: number;
}

export function TrendChart({ 
  data, 
  dataKey, 
  xAxisKey, 
  color = '#0ea5e9',
  type = 'area',
  height = 300 
}: TrendChartProps) {
  const ChartComponent = type === 'area' ? AreaChart : LineChart;
  const DataComponent: any = type === 'area' ? Area : Line;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ChartComponent data={data}>
        <defs>
          <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
            <stop offset="95%" stopColor={color} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey={xAxisKey} 
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
          }}
        />
        <DataComponent
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          fill={type === 'area' ? 'url(#colorGradient)' : undefined}
          strokeWidth={2}
        />
      </ChartComponent>
    </ResponsiveContainer>
  );
}
