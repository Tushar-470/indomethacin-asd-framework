import React, { useEffect, useState } from 'react';
import { fetchDrugs, fetchPolymers, runScreening } from '../api';
import { useNavigate } from 'react-router-dom';

export default function Screening() {
  const [drugs, setDrugs] = useState<any[]>([]);
  const [polymers, setPolymers] = useState<any[]>([]);
  const [selectedDrug, setSelectedDrug] = useState('');
  const [selectedPolymers, setSelectedPolymers] = useState<string[]>([]);
  const [mode, setMode] = useState('research');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDrugs().then(setDrugs).catch(console.error);
    fetchPolymers().then(setPolymers).catch(console.error);
  }, []);

  const handleTogglePolymer = (id: string) => {
    setSelectedPolymers(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  };

  const handleRun = async () => {
    if (!selectedDrug || selectedPolymers.length < 2) return;
    setLoading(true);
    try {
      const res = await runScreening({
        drug_id: selectedDrug,
        polymer_ids: selectedPolymers,
        mode,
        drug_loading: 0.3,
        random_seed: 42
      });
      navigate(`/results/${res.id}`);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="header">
        <h1 className="title">Screening Configuration</h1>
      </div>
      <div className="card">
        <h3>1. Select Drug</h3>
        <select value={selectedDrug} onChange={e => setSelectedDrug(e.target.value)} style={{ padding: '0.5rem', width: '100%', marginBottom: '1rem', background: 'var(--bg)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>
          <option value="">-- Select a Drug --</option>
          {drugs.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>

        <h3>2. Select Polymers (Min 2)</h3>
        <div style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: '1rem', border: '1px solid var(--border)', padding: '0.5rem' }}>
          {polymers.map(p => (
            <div key={p.id} style={{ marginBottom: '0.5rem' }}>
              <label>
                <input type="checkbox" checked={selectedPolymers.includes(p.id)} onChange={() => handleTogglePolymer(p.id)} />
                <span style={{ marginLeft: '0.5rem' }}>{p.name} ({p.abbreviation})</span>
              </label>
            </div>
          ))}
        </div>

        <h3>3. Mode</h3>
        <select value={mode} onChange={e => setMode(e.target.value)} style={{ padding: '0.5rem', width: '100%', marginBottom: '1rem', background: 'var(--bg)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>
          <option value="research">Research (Rigorous analysis)</option>
          <option value="exploratory">Exploratory (Fast prediction)</option>
        </select>

        <button className="btn" onClick={handleRun} disabled={loading || !selectedDrug || selectedPolymers.length < 2}>
          {loading ? 'Running...' : 'Run Screening'}
        </button>
      </div>
    </div>
  );
}
