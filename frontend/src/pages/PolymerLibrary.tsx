import React, { useEffect, useState } from 'react';
import { fetchPolymers, createPolymer } from '../api';

export default function PolymerLibrary() {
  const [polymers, setPolymers] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    polymer_id: '',
    polymer_name: '',
    abbreviation: '',
    mn_da: 50000.0,
    tg_k: 380.0,
    density_g_cm3: 1.20,
    hsp_delta_d: 17.5,
    hsp_delta_p: 8.0,
    hsp_delta_h: 10.0,
    functional_groups: 'ester|ether',
    monomer_smiles: 'C=CC(=O)O',
    literature_evidence_score: 0.5,
    validation_status: 'draft'
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [saving, setSaving] = useState(false);

  const loadPolymers = () => {
    fetchPolymers().then(setPolymers).catch(err => setErrorMsg(err.message));
  };

  useEffect(() => {
    loadPolymers();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    try {
      await createPolymer({
        ...formData,
        mn_da: Number(formData.mn_da),
        tg_k: Number(formData.tg_k),
        density_g_cm3: Number(formData.density_g_cm3),
        hsp_delta_d: Number(formData.hsp_delta_d),
        hsp_delta_p: Number(formData.hsp_delta_p),
        hsp_delta_h: Number(formData.hsp_delta_h),
        literature_evidence_score: Number(formData.literature_evidence_score)
      });
      setShowModal(false);
      loadPolymers();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to add polymer profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="title">Polymer Carrier Library</h1>
        <button className="btn" onClick={() => setShowModal(true)}>+ Add New Polymer Carrier</button>
      </div>

      {errorMsg && (
        <div className="card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)', marginBottom: '1rem' }}>
          {errorMsg}
        </div>
      )}

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Polymer ID</th>
                <th>Polymer Name</th>
                <th>Abbreviation</th>
                <th>Mn (Da)</th>
                <th>Tg (K)</th>
                <th>Density (g/cm³)</th>
                <th>HSP (δD / δP / δH)</th>
                <th>Lit Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {polymers.map(poly => (
                <tr key={poly.polymer_id}>
                  <td><strong>{poly.polymer_id}</strong></td>
                  <td>{poly.polymer_name}</td>
                  <td><span className="badge primary">{poly.abbreviation}</span></td>
                  <td>{poly.mn_da?.toLocaleString()}</td>
                  <td>{poly.tg_k}</td>
                  <td>{poly.density_g_cm3}</td>
                  <td>{poly.hsp_delta_d} / {poly.hsp_delta_p} / {poly.hsp_delta_h}</td>
                  <td>{poly.literature_evidence_score}</td>
                  <td>
                    <span className={`badge ${poly.is_reference ? 'success' : 'warning'}`}>
                      {poly.is_reference ? 'Reference (Validated)' : 'User (Draft)'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div className="card" style={{ width: '520px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2>Add New Polymer Carrier</h2>
            <form onSubmit={handleSave} style={{ display: 'grid', gap: '0.75rem', marginTop: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Polymer ID *</label>
                <input required type="text" placeholder="e.g. POL-007-2026" value={formData.polymer_id} onChange={e => setFormData({ ...formData, polymer_id: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Full Polymer Name *</label>
                <input required type="text" placeholder="e.g. Polyethylene Glycol 6000" value={formData.polymer_name} onChange={e => setFormData({ ...formData, polymer_name: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Abbreviation *</label>
                <input required type="text" placeholder="e.g. PEG_6000" value={formData.abbreviation} onChange={e => setFormData({ ...formData, abbreviation: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Monomer SMILES * (pipe | for copolymer)</label>
                <input required type="text" placeholder="e.g. C=CC(=O)O" value={formData.monomer_smiles} onChange={e => setFormData({ ...formData, monomer_smiles: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>Mn (Da)</label>
                  <input type="number" step="100" value={formData.mn_da} onChange={e => setFormData({ ...formData, mn_da: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>Glass Transition Tg (K)</label>
                  <input type="number" step="0.1" value={formData.tg_k} onChange={e => setFormData({ ...formData, tg_k: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>HSP δD</label>
                  <input type="number" step="0.1" value={formData.hsp_delta_d} onChange={e => setFormData({ ...formData, hsp_delta_d: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>HSP δP</label>
                  <input type="number" step="0.1" value={formData.hsp_delta_p} onChange={e => setFormData({ ...formData, hsp_delta_p: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>HSP δH</label>
                  <input type="number" step="0.1" value={formData.hsp_delta_h} onChange={e => setFormData({ ...formData, hsp_delta_h: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="submit" className="btn" disabled={saving} style={{ flex: 1 }}>{saving ? 'Saving...' : 'Save Polymer Carrier'}</button>
                <button type="button" className="btn" onClick={() => setShowModal(false)} style={{ background: 'transparent', border: '1px solid var(--border)' }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
