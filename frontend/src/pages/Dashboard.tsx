import React, { useEffect, useState } from 'react';
import { fetchHistory } from '../api';
import { Link } from 'react-router-dom';

export default function Dashboard({ version }: { version: any }) {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    fetchHistory().then(data => setHistory(data.slice(0, 5))).catch(console.error);
  }, []);

  return (
    <div>
      <div className="header">
        <h1 className="title">Dashboard Overview</h1>
      </div>

      <div className="card" style={{ background: 'linear-gradient(135deg, var(--surface) 0%, rgba(79,143,247,0.15) 100%)', marginBottom: '1.5rem', border: '1px solid var(--primary)' }}>
        <h2 style={{ margin: '0 0 0.5rem 0' }}>Quality by Design Polymer Screening Engine</h2>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
          Integrated computational polymer screening and failure boundary mapping framework for amorphous solid dispersions.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <Link to="/screening" className="card" style={{ textDecoration: 'none', border: '1px solid var(--primary)' }}>
          <div style={{ fontSize: '1.8rem', marginBottom: '0.4rem' }}>🚀</div>
          <h3 style={{ margin: 0, color: 'var(--primary)' }}>Start Screening</h3>
          <small style={{ color: 'var(--text-secondary)' }}>Run 11-step polymer ranking</small>
        </Link>

        <Link to="/drugs" className="card" style={{ textDecoration: 'none' }}>
          <div style={{ fontSize: '1.8rem', marginBottom: '0.4rem' }}>💊</div>
          <h3 style={{ margin: 0 }}>Drug API Library</h3>
          <small style={{ color: 'var(--text-secondary)' }}>View physicochemical profiles</small>
        </Link>

        <Link to="/polymers" className="card" style={{ textDecoration: 'none' }}>
          <div style={{ fontSize: '1.8rem', marginBottom: '0.4rem' }}>🧪</div>
          <h3 style={{ margin: 0 }}>Polymer Carriers</h3>
          <small style={{ color: 'var(--text-secondary)' }}>Explore polymer library</small>
        </Link>

        <Link to="/history" className="card" style={{ textDecoration: 'none' }}>
          <div style={{ fontSize: '1.8rem', marginBottom: '0.4rem' }}>📜</div>
          <h3 style={{ margin: 0 }}>Audit History</h3>
          <small style={{ color: 'var(--text-secondary)' }}>Past analysis records</small>
        </Link>
      </div>

      <div className="card">
        <h3>Recent Screening Analyses</h3>
        {history.length > 0 ? (
          <div className="table-container" style={{ marginTop: '1rem' }}>
            <table>
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Date</th>
                  <th>Drug</th>
                  <th>Top Selection</th>
                  <th>TOPSIS CL</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {history.map(item => (
                  <tr key={item.analysis_id}>
                    <td><strong style={{ fontSize: '0.85rem' }}>{item.analysis_id}</strong></td>
                    <td>{new Date(item.created_at || item.timestamp).toLocaleDateString()}</td>
                    <td>{item.drug_name || item.drug_id}</td>
                    <td><strong style={{ color: 'var(--primary)' }}>{item.top_polymer}</strong></td>
                    <td>{item.topsis_cl ? item.topsis_cl.toFixed(4) : 'N/A'}</td>
                    <td>
                      <Link to={`/results/${item.analysis_id}`} className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>No recent analyses found.</p>
        )}
      </div>
    </div>
  );
}
