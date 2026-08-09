import React, { useEffect, useState } from 'react';
import { fetchHistory } from '../api';
import { Link } from 'react-router-dom';

export default function History() {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    fetchHistory().then(setHistory).catch(console.error);
  }, []);

  return (
    <div>
      <div className="header">
        <h1 className="title">Analysis History</h1>
      </div>
      <div className="card">
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
                  <td><Link to={`/results/${item.id}`} className="btn">View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
