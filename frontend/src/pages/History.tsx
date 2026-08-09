import React, { useEffect, useState } from 'react';
import { fetchHistory, deleteHistory } from '../api';
import { Link } from 'react-router-dom';

export default function History() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const loadHistory = () => {
    setLoading(true);
    fetchHistory()
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(err => {
        setErrorMsg(err.message || 'Failed to load analysis history.');
        setLoading(false);
      });
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (analysisId: string) => {
    if (!window.confirm(`Delete analysis record '${analysisId}'?`)) return;
    try {
      await deleteHistory(analysisId);
      loadHistory();
    } catch (err: any) {
      alert(err.message || 'Failed to delete record.');
    }
  };

  return (
    <div>
      <div className="header">
        <h1 className="title">Analysis Audit Trail & History</h1>
      </div>

      {errorMsg && (
        <div className="card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)', marginBottom: '1rem' }}>
          {errorMsg}
        </div>
      )}

      <div className="card">
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading analysis history...
          </div>
        ) : history.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No past screening analyses found. Run a screening from the <Link to="/screening" style={{ color: 'var(--primary)' }}>Screening Workspace</Link>.
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Date / Time</th>
                  <th>Drug API</th>
                  <th>Polymers</th>
                  <th>Mode</th>
                  <th>Top Selection</th>
                  <th>TOPSIS CL</th>
                  <th>Confidence</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {history.map(item => (
                  <tr key={item.analysis_id}>
                    <td><strong style={{ fontSize: '0.85rem' }}>{item.analysis_id}</strong></td>
                    <td>{new Date(item.created_at || item.timestamp).toLocaleString()}</td>
                    <td>{item.drug_name || item.drug_id}</td>
                    <td>{item.polymer_ids?.length} screened</td>
                    <td>
                      <span className={`badge ${item.mode === 'research' ? 'success' : 'warning'}`}>
                        {item.mode ? item.mode.toUpperCase() : 'UNKNOWN'}
                      </span>
                    </td>
                    <td><strong style={{ color: 'var(--primary)' }}>{item.top_polymer}</strong></td>
                    <td>{item.topsis_cl ? item.topsis_cl.toFixed(4) : 'N/A'}</td>
                    <td><span className="badge primary">{item.confidence_tier || 'N/A'}</span></td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <Link to={`/results/${item.analysis_id}`} className="btn" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}>
                        View Results
                      </Link>
                      <button
                        className="btn"
                        onClick={() => handleDelete(item.analysis_id)}
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', background: 'transparent', border: '1px solid var(--danger)', color: 'var(--danger)' }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
