import React, { useEffect, useState } from 'react';
import { fetchDrugs, fetchPolymers, runScreening } from '../api';
import { useNavigate } from 'react-router-dom';

export default function Screening() {
  const [drugs, setDrugs] = useState<any[]>([]);
  const [polymers, setPolymers] = useState<any[]>([]);
  const [selectedDrug, setSelectedDrug] = useState('');
  const [selectedPolymers, setSelectedPolymers] = useState<string[]>([]);
  const [mode, setMode] = useState<'research' | 'exploratory'>('exploratory');
  const [drugLoading, setDrugLoading] = useState(0.30);
  const [randomSeed, setRandomSeed] = useState(42);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchDrugs().then(data => {
      setDrugs(data);
      if (data.length > 0) setSelectedDrug(data[0].drug_id);
    }).catch(err => setErrorMsg(err.message));

    fetchPolymers().then(data => {
      setPolymers(data);
      // Pre-select all polymers by default
      setSelectedPolymers(data.map((p: any) => p.polymer_id));
    }).catch(err => setErrorMsg(err.message));
  }, []);

  const handleTogglePolymer = (polymerId: string) => {
    if (!polymerId) return;
    setSelectedPolymers(prev =>
      prev.includes(polymerId)
        ? prev.filter(id => id !== polymerId)
        : [...prev, polymerId]
    );
  };

  const handleSelectAll = () => {
    setSelectedPolymers(polymers.map(p => p.polymer_id));
  };

  const handleClearAll = () => {
    setSelectedPolymers([]);
  };

  const filteredPolymers = polymers.filter(p =>
    (p.polymer_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (p.abbreviation || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (p.polymer_id || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleRun = async () => {
    if (!selectedDrug || selectedPolymers.length < 2) {
      setErrorMsg('Please select a drug and at least 2 polymers.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const res = await runScreening({
        drug_id: selectedDrug,
        polymer_ids: selectedPolymers,
        mode: mode,
        drug_loading_ww: Number(drugLoading),
        random_seed: Number(randomSeed)
      });

      if (res && res.analysis_id) {
        navigate(`/results/${res.analysis_id}`);
      } else {
        throw new Error('Analysis completed but no analysis_id was returned.');
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Screening pipeline failed.');
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="header">
        <h1 className="title">Computational Screening Workspace</h1>
      </div>

      {errorMsg && (
        <div className="card" style={{ borderColor: 'var(--danger)', backgroundColor: 'rgba(239,68,68,0.1)', color: 'var(--danger)', marginBottom: '1.5rem' }}>
          <strong>Error:</strong> {errorMsg}
        </div>
      )}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>1. Select Active Pharmaceutical Ingredient (Drug API)</h3>
        <select
          id="drug-select"
          value={selectedDrug}
          onChange={e => setSelectedDrug(e.target.value)}
          style={{
            padding: '0.75rem',
            width: '100%',
            marginTop: '0.5rem',
            background: 'var(--bg)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            fontSize: '1rem'
          }}
        >
          <option value="">-- Select Drug Profile --</option>
          {drugs.map(d => (
            <option key={d.drug_id} value={d.drug_id}>
              {d.generic_name} ({d.drug_id}) - Tm: {d.tm_k}K, Tg: {d.tg_k || d.tg_k_estimated}K
            </option>
          ))}
        </select>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3>2. Select Candidate Polymers ({selectedPolymers.length} of {polymers.length} selected)</h3>
          <div>
            <button className="btn" style={{ padding: '0.3rem 0.75rem', fontSize: '0.85rem', marginRight: '0.5rem' }} onClick={handleSelectAll}>Select All</button>
            <button className="btn" style={{ padding: '0.3rem 0.75rem', fontSize: '0.85rem', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-secondary)' }} onClick={handleClearAll}>Clear</button>
          </div>
        </div>

        <input
          type="text"
          placeholder="Filter polymers by name, abbreviation, or ID..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          style={{
            padding: '0.5rem 0.75rem',
            width: '100%',
            marginBottom: '1rem',
            background: 'var(--bg)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            borderRadius: '4px'
          }}
        />

        <div style={{ maxHeight: '250px', overflowY: 'auto', border: '1px solid var(--border)', borderRadius: '6px', padding: '0.5rem' }}>
          {filteredPolymers.map(p => {
            const isChecked = selectedPolymers.includes(p.polymer_id);
            return (
              <div key={p.polymer_id} style={{ display: 'flex', alignItems: 'center', padding: '0.4rem 0.6rem', borderBottom: '1px solid rgba(255,255,255,0.05)', background: isChecked ? 'rgba(79,143,247,0.08)' : 'transparent' }}>
                <input
                  id={`poly-check-${p.polymer_id}`}
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => handleTogglePolymer(p.polymer_id)}
                  style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                />
                <label htmlFor={`poly-check-${p.polymer_id}`} style={{ marginLeft: '0.75rem', cursor: 'pointer', flex: 1 }}>
                  <strong>{p.polymer_name}</strong> ({p.abbreviation}) — <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Mn: {p.mn_da} Da | Tg: {p.tg_k}K | δD/δP/δH: {p.hsp_delta_d}/{p.hsp_delta_p}/{p.hsp_delta_h}</span>
                </label>
                <span className={`badge ${p.is_reference ? 'success' : 'primary'}`} style={{ fontSize: '0.75rem' }}>
                  {p.is_reference ? 'Validated' : 'Draft'}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>3. Execution Parameters & Mode</h3>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Execution Mode</label>
            <select
              value={mode}
              onChange={e => setMode(e.target.value as any)}
              style={{
                padding: '0.6rem',
                width: '100%',
                background: 'var(--bg)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border)',
                borderRadius: '6px'
              }}
            >
              <option value="research">Research Mode (Strict data validation required)</option>
              <option value="exploratory">Exploratory Mode (Allows custom/draft data)</option>
            </select>
            <small style={{ color: 'var(--text-secondary)', display: 'block', marginTop: '0.4rem' }}>
              {mode === 'research' ? 'Requires all inputs to have validated status.' : 'Permits unvalidated draft profiles with warning badges.'}
            </small>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Target Drug Loading: {(drugLoading * 100).toFixed(0)}% w/w
            </label>
            <input
              type="range"
              min="0.05"
              max="0.60"
              step="0.05"
              value={drugLoading}
              onChange={e => setDrugLoading(parseFloat(e.target.value))}
              style={{ width: '100%' }}
            />
            <small style={{ color: 'var(--text-secondary)', display: 'block', marginTop: '0.4rem' }}>
              Mass fraction of API in spray-dried matrix. Standard default: 30% w/w.
            </small>
          </div>
        </div>
      </div>

      <button
        className="btn"
        onClick={handleRun}
        disabled={loading || !selectedDrug || selectedPolymers.length < 2}
        style={{
          width: '100%',
          padding: '1rem',
          fontSize: '1.1rem',
          fontWeight: 700,
          background: loading ? 'var(--text-secondary)' : 'var(--primary)',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? (
          <span>⚡ Running 11-Step Computational Screening Pipeline (HSP, FH, GT, PCA, AHP, TOPSIS, UQ, SA, FBM)...</span>
        ) : (
          `🚀 Run Polymer Screening (${selectedPolymers.length} Candidates)`
        )}
      </button>
    </div>
  );
}
