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
        <h1 className="title">Dashboard</h1>
      </div>
      <div className="card" style={{ background: 'linear-gradient(45deg, var(--surface), rgba(79,143,247,0.1))' }}>
        <h2>Welcome to ASD Framework</h2>
        <p>Scientific Amorphous Solid Dispersion Screening Engine.</p>
      </div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <Link to="/screening" className="card" style={{ flex: 1, textAlign: 'center' }}>
          <h3>Start Screening</h3>
        </Link>
        <Link to="/drugs" className="card" style={{ flex: 1, textAlign: 'center' }}>
          <h3>View Drug Library</h3>
        </Link>
        <Link to="/polymers" className="card" style={{ flex: 1, textAlign: 'center' }}>
          <h3>View Polymers</h3>
        </Link>
      </div>
      <div className="card">
        <h3>Recent Analyses</h3>
        {history.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Drug</th>
                  <th>Mode</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {history.map(item => (
                  <tr key={item.id}>
                    <td>{new Date(item.created_at).toLocaleDateString()}</td>
                    <td>{item.drug_id}</td>
                    <td><span className="badge primary">{item.mode}</span></td>
                    <td><Link to={`/results/${item.id}`}>View</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No recent analyses found.</p>
        )}
      </div>
    </div>
  );
}
