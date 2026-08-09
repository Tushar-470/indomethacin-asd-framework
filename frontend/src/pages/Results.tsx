import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchScreeningResult } from '../api';

export default function Results() {
  const { id } = useParams();
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (id) {
      fetchScreeningResult(id).then(setResult).catch(console.error);
    }
  }, [id]);

  if (!result) return <div style={{ padding: '2rem' }}>Loading results...</div>;

  return (
    <div>
      <div className="header">
        <h1 className="title">Screening Results</h1>
        <span className={`badge ${result.mode === 'research' ? 'success' : 'warning'}`}>{result.mode.toUpperCase()} MODE</span>
      </div>
      <div className="card">
        <h3>Top Polymer: {result.top_polymer?.name || result.rankings[0]?.polymer_id}</h3>
        <p>CL: {result.rankings[0]?.cl_score}</p>
        <p>Confidence: {result.rankings[0]?.confidence_tier}</p>
      </div>
      <div className="card">
        <h3>Rankings</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Polymer</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {result.rankings.map((r: any, idx: number) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td>{r.polymer_id}</td>
                  <td>{r.cl_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
