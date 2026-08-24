import React from 'react';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface VarianceChartProps {
  components: string[];
  variance: number[];
  cumulativeVariance?: number[];
}

const VarianceChart: React.FC<VarianceChartProps> = ({ components, variance, cumulativeVariance }) => {
  const data = components.map((comp, idx) => ({
    name: comp,
    variance: variance[idx],
    cumulative: cumulativeVariance ? cumulativeVariance[idx] : undefined,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <ComposedChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis dataKey="name" tick={{ fontSize: 12, fontFamily: 'var(--font-primary)' }} />
        <YAxis tick={{ fontSize: 12, fontFamily: 'var(--font-mono)' }} yAxisId="left" />
        {cumulativeVariance && (
          <YAxis tick={{ fontSize: 12, fontFamily: 'var(--font-mono)' }} yAxisId="right" orientation="right" />
        )}
        <Tooltip wrapperStyle={{ fontFamily: 'var(--font-primary)', fontSize: 12 }} />
        <Bar dataKey="variance" name="Explained Variance %" fill="var(--color-primary-action)" yAxisId="left" />
        {cumulativeVariance && (
          <Line type="monotone" dataKey="cumulative" name="Cumulative Variance %" stroke="var(--color-warning)" yAxisId="right" />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default VarianceChart;
