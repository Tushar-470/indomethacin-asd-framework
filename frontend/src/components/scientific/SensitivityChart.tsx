import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface SensitivityChartProps {
  featureNames: string[];
  mu: number[];
  sigma: number[];
}

const SensitivityChart: React.FC<SensitivityChartProps> = ({ featureNames, mu, sigma }) => {
  const data = featureNames.map((name, idx) => ({
    name,
    mu: mu[idx],
    sigma: sigma[idx],
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis type="number" tick={{ fontSize: 12, fontFamily: 'var(--font-mono)' }} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fontFamily: 'var(--font-primary)' }} width={100} />
        <Tooltip wrapperStyle={{ fontFamily: 'var(--font-primary)', fontSize: 12 }} />
        <Legend wrapperStyle={{ fontFamily: 'var(--font-primary)', fontSize: 12 }} />
        <Bar dataKey="mu" name="μ* (Mean)" fill="var(--color-primary-action)" />
        <Bar dataKey="sigma" name="σ (Std Dev)" fill="var(--color-warning)" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SensitivityChart;
