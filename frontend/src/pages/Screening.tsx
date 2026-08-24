import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDrugs, fetchPolymers, runScreening } from '../api';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingState from '../components/ui/LoadingState';
import { Play, Search, AlertCircle, Sliders, CheckCircle2 } from 'lucide-react';

export default function Screening() {
  const navigate = useNavigate();
  const [drugs, setDrugs] = useState<any[]>([]);
  const [polymers, setPolymers] = useState<any[]>([]);
  
  const [selectedDrug, setSelectedDrug] = useState<string>('');
  const [selectedPolymers, setSelectedPolymers] = useState<string[]>([]);
  const [mode, setMode] = useState<'research' | 'exploratory'>('exploratory');
  const [drugLoading, setDrugLoading] = useState<number>(0.30);
  const [randomSeed, setRandomSeed] = useState<number>(42);
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [executing, setExecuting] = useState<boolean>(false);

  useEffect(() => {
    Promise.all([
      fetchDrugs().catch(() => []),
      fetchPolymers().catch(() => [])
    ])
      .then(([drugsData, polymersData]) => {
        const dList = Array.isArray(drugsData) ? drugsData : [];
        const pList = Array.isArray(polymersData) ? polymersData : [];
        setDrugs(dList);
        setPolymers(pList);
        if (dList.length > 0) {
          setSelectedDrug(dList[0].drug_id || dList[0].id || '');
        }
        // Pre-select all candidate polymers by default
        setSelectedPolymers(pList.map(p => p.polymer_id || p.id));
        setLoading(false);
      })
      .catch(err => {
        setErrorMsg(err.message || 'Failed to initialize workspace data.');
        setLoading(false);
      });
  }, []);

  const handleSelectAll = () => {
    setSelectedPolymers(filteredPolymers.map(p => p.polymer_id || p.id));
  };
  
  const handleClearAll = () => {
    setSelectedPolymers([]);
  };
  
  const togglePolymer = (id: string) => {
    setSelectedPolymers(prev => 
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    );
  };

  const handleLaunch = async () => {
    if (!selectedDrug || selectedPolymers.length < 2) {
      setErrorMsg('Please select a drug API and at least 2 candidate polymers.');
      return;
    }
    setExecuting(true);
    setErrorMsg('');
    try {
      const res = await runScreening({
        drug_id: selectedDrug,
        polymer_ids: selectedPolymers,
        mode,
        drug_loading_ww: Number(drugLoading),
        random_seed: Number(randomSeed)
      });
      if (res && res.analysis_id) {
        navigate(`/results/${res.analysis_id}`);
      } else {
        throw new Error('Pipeline completed but no analysis_id was returned.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Pipeline execution failed.');
      setExecuting(false);
    }
  };

  if (loading) return <LoadingState message="Loading computational screening workspace..." />;

  const filteredPolymers = polymers.filter(p => {
    const pName = p.polymer_name || p.name || '';
    const abbr = p.abbreviation || '';
    const pId = p.polymer_id || p.id || '';
    return pName.toLowerCase().includes(searchTerm.toLowerCase()) || 
           abbr.toLowerCase().includes(searchTerm.toLowerCase()) ||
           pId.toLowerCase().includes(searchTerm.toLowerCase());
  });
  
  const activeDrug = drugs.find(d => (d.drug_id || d.id) === selectedDrug);

  return (
    <div className="page-container">
      <header className="header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Play size={24} style={{ color: 'var(--color-primary-action)' }} />
            <h1 className="title" style={{ margin: 0 }}>Computational Screening Workspace</h1>
          </div>
          <p style={{ color: 'var(--color-secondary-text)', margin: 0 }}>
            Execute 11-step thermodynamic, dimensional reduction, and MCDA polymer selection pipeline
          </p>
        </div>
      </header>
      
      {errorMsg && (
        <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Step 1 */}
        <div className="card" style={{ margin: 0 }}>
          <div className="step-header">
            <div className="step-number">1</div>
            <div>
              <div className="step-title">Active Pharmaceutical Ingredient (Drug API)</div>
              <div className="step-subtitle">Select API physicochemical profile</div>
            </div>
          </div>
          
          <select 
            style={{ width: '100%', padding: '0.6rem', marginBottom: '1rem' }}
            value={selectedDrug}
            onChange={e => setSelectedDrug(e.target.value)}
          >
            <option value="">-- Select a Drug Profile --</option>
            {drugs.map(d => {
              const dId = d.drug_id || d.id;
              const dName = d.generic_name || d.name;
              const mw = d.molecular_weight_g_mol ?? d.mw;
              const tm = d.tm_k ?? d.tm;
              const tg = d.tg_k ?? d.tg ?? d.tg_k_estimated;
              return (
                <option key={dId} value={dId}>
                  {dName} ({dId}) — MW: {mw} | Tm: {tm}K | Tg: {tg}K
                </option>
              );
            })}
          </select>
          
          {activeDrug && (
            <div style={{ backgroundColor: 'var(--color-surface-subtle)', padding: '0.75rem', borderRadius: '4px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '12px' }}>
              <div>
                <span style={{ color: 'var(--color-muted-text)', fontSize: '10px', textTransform: 'uppercase', display: 'block' }}>GENERIC NAME</span>
                <strong>{activeDrug.generic_name || activeDrug.name}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-muted-text)', fontSize: '10px', textTransform: 'uppercase', display: 'block' }}>BCS CLASS</span>
                <strong>Class {activeDrug.bcs_class || 'II'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-muted-text)', fontSize: '10px', textTransform: 'uppercase', display: 'block' }}>MW / TM / TG</span>
                <span className="mono">{activeDrug.molecular_weight_g_mol || activeDrug.mw} / {activeDrug.tm_k}K / {activeDrug.tg_k || activeDrug.tg_k_estimated}K</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-muted-text)', fontSize: '10px', textTransform: 'uppercase', display: 'block' }}>HSP & R₀</span>
                <span className="mono">{activeDrug.hsp_delta_d}/{activeDrug.hsp_delta_p}/{activeDrug.hsp_delta_h} (R₀: {activeDrug.hsp_ro || 8.0})</span>
              </div>
            </div>
          )}
        </div>
        
        {/* Step 3 */}
        <div className="card" style={{ margin: 0 }}>
          <div className="step-header">
            <div className="step-number">2</div>
            <div>
              <div className="step-title">Execution Parameters & Mode</div>
              <div className="step-subtitle">Formulation loading & uncertainty settings</div>
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label className="form-label">Execution Mode</label>
              <select 
                value={mode} 
                onChange={e => setMode(e.target.value as any)}
                style={{ width: '100%', padding: '0.5rem' }}
              >
                <option value="research">Research Mode (Strict validation required)</option>
                <option value="exploratory">Exploratory Mode (Allows custom / draft candidates)</option>
              </select>
              <span className="form-help">
                {mode === 'research' ? 'Ensures all candidates meet publication-grade evidentiary validation.' : 'Permits screening newly added draft polymers and user profiles.'}
              </span>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label className="form-label" style={{ margin: 0 }}>Target Drug Loading</label>
                <strong className="mono" style={{ color: 'var(--color-primary-action)' }}>{(drugLoading * 100).toFixed(0)}% w/w</strong>
              </div>
              <input 
                type="range" 
                min="0.05" 
                max="0.60" 
                step="0.05"
                value={drugLoading}
                onChange={e => setDrugLoading(parseFloat(e.target.value))}
                style={{ width: '100%', marginTop: '4px' }}
              />
              <span className="form-help">Mass fraction of API in matrix (default: 30% w/w).</span>
            </div>

            <div>
              <label className="form-label">Random Seed (Monte Carlo UQ)</label>
              <input 
                type="number" 
                value={randomSeed}
                onChange={e => setRandomSeed(parseInt(e.target.value) || 42)}
                style={{ width: '100%', padding: '0.4rem' }}
              />
              <span className="form-help">Fixed random seed for exact reproducibility (default: 42).</span>
            </div>
          </div>
        </div>
      </div>

      {/* Step 2: Candidates */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="step-header">
          <div className="step-number">3</div>
          <div style={{ flex: 1 }}>
            <div className="step-title">
              Candidate Polymer Selection ({selectedPolymers.length} of {polymers.length} Selected)
            </div>
            <div className="step-subtitle">Select excipient library candidates for ranking</div>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            <Button variant="secondary" size="sm" onClick={handleSelectAll}>Select All</Button>
            <Button variant="secondary" size="sm" onClick={handleClearAll}>Clear</Button>
          </div>
        </div>

        <div style={{ marginBottom: '1rem', position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-muted-text)' }} />
          <input 
            type="text" 
            placeholder="Filter candidates by name, abbreviation, or ID..." 
            style={{ width: '100%', paddingLeft: '30px', height: '34px' }}
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={{ maxHeight: '280px', overflowY: 'auto', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
          {filteredPolymers.map(p => {
            const pId = p.polymer_id || p.id;
            const pName = p.polymer_name || p.name;
            const abbr = p.abbreviation || 'N/A';
            const mn = p.mn_da ?? p.mn;
            const tg = p.tg_k ?? p.tg;
            const isChecked = selectedPolymers.includes(pId);

            return (
              <div 
                key={pId}
                onClick={() => togglePolymer(pId)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.6rem 0.75rem',
                  borderBottom: '1px solid var(--color-border)',
                  cursor: 'pointer',
                  backgroundColor: isChecked ? 'var(--color-surface-subtle)' : 'transparent',
                  transition: 'background-color 0.15s'
                }}
              >
                <input 
                  type="checkbox" 
                  checked={isChecked} 
                  onChange={() => {}} 
                  style={{ width: '16px', height: '16px', marginRight: '10px', cursor: 'pointer' }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <strong style={{ fontSize: '13px' }}>{pName}</strong>
                    <Badge variant="primary">{abbr}</Badge>
                    <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted-text)' }}>{pId}</span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-secondary-text)', marginTop: '2px' }}>
                    Mn: {typeof mn === 'number' ? mn.toLocaleString() : mn} Da | Tg: {tg} K | HSP: {p.hsp_delta_d}/{p.hsp_delta_p}/{p.hsp_delta_h}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Launch Action */}
      <div className="card" style={{ textAlign: 'center', padding: '1.5rem', backgroundColor: 'var(--color-surface)' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <Button 
            variant="primary" 
            size="lg" 
            disabled={executing || !selectedDrug || selectedPolymers.length < 2}
            onClick={handleLaunch}
            style={{ width: '100%', padding: '0.85rem', fontSize: '15px', fontWeight: 600 }}
          >
            {executing ? (
              <span>⚡ Executing 11-Step Pipeline (HSP, Flory-Huggins, Gordon-Taylor, PCA, AHP, TOPSIS, Monte Carlo UQ)...</span>
            ) : (
              <span>🚀 Execute Computational Screening Pipeline ({selectedPolymers.length} Candidates)</span>
            )}
          </Button>
          <div style={{ fontSize: '12px', color: 'var(--color-muted-text)', marginTop: '0.5rem' }}>
            Requires minimum 2 candidate polymers. Full execution includes sensitivity analysis & failure boundary mapping.
          </div>
        </div>
      </div>
    </div>
  );
}
