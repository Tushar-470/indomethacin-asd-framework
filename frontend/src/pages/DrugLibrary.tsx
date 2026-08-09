import React, { useEffect, useState } from 'react';
import { fetchDrugs, createDrug } from '../api';

export default function DrugLibrary() {
  const [drugs, setDrugs] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    drug_id: '',
    generic_name: '',
    canonical_smiles: '',
    molecular_weight_g_mol: 350.0,
    tm_k: 420.0,
    tg_k: 310.0,
    bcs_class: 'II',
    hsp_delta_d: 18.5,
    hsp_delta_p: 7.5,
    hsp_delta_h: 8.5,
    hsp_ro: 8.0,
    molar_volume_cm3_mol: 270.0,
    reference_source: 'user_entered',
    validation_status: 'draft'
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [saving, setSaving] = useState(false);

  const loadDrugs = () => {
    fetchDrugs().then(setDrugs).catch(err => setErrorMsg(err.message));
  };

  useEffect(() => {
    loadDrugs();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    try {
      await createDrug({
        ...formData,
        molecular_weight_g_mol: Number(formData.molecular_weight_g_mol),
        tm_k: Number(formData.tm_k),
        tg_k: Number(formData.tg_k),
        hsp_delta_d: Number(formData.hsp_delta_d),
        hsp_delta_p: Number(formData.hsp_delta_p),
        hsp_delta_h: Number(formData.hsp_delta_h),
        hsp_ro: Number(formData.hsp_ro),
        molar_volume_cm3_mol: Number(formData.molar_volume_cm3_mol)
      });
      setShowModal(false);
      loadDrugs();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to add drug profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="title">Drug API Library</h1>
        <button className="btn" onClick={() => setShowModal(true)}>+ Add New Drug Profile</button>
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
                <th>Drug ID</th>
                <th>Generic Name</th>
                <th>MW (g/mol)</th>
                <th>Tm (K)</th>
                <th>Tg (K)</th>
                <th>BCS</th>
                <th>HSP (δD / δP / δH)</th>
                <th>Radius R₀</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {drugs.map(drug => (
                <tr key={drug.drug_id}>
                  <td><strong>{drug.drug_id}</strong></td>
                  <td>{drug.generic_name}</td>
                  <td>{drug.molecular_weight_g_mol}</td>
                  <td>{drug.tm_k}</td>
                  <td>{drug.tg_k || (drug.tg_k_estimated ? `${drug.tg_k_estimated} (est)` : 'N/A')}</td>
                  <td><span className="badge primary">{drug.bcs_class}</span></td>
                  <td>{drug.hsp_delta_d} / {drug.hsp_delta_p} / {drug.hsp_delta_h}</td>
                  <td>{drug.hsp_ro}</td>
                  <td>
                    <span className={`badge ${drug.is_reference ? 'success' : 'warning'}`}>
                      {drug.is_reference ? 'Reference (Validated)' : 'User (Draft)'}
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
          <div className="card" style={{ width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2>Add New Drug Profile</h2>
            <form onSubmit={handleSave} style={{ display: 'grid', gap: '0.75rem', marginTop: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Drug ID *</label>
                <input required type="text" placeholder="e.g. NAP-001-2026" value={formData.drug_id} onChange={e => setFormData({ ...formData, drug_id: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Generic Name *</label>
                <input required type="text" placeholder="e.g. Naproxen" value={formData.generic_name} onChange={e => setFormData({ ...formData, generic_name: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem' }}>Canonical SMILES *</label>
                <input required type="text" placeholder="SMILES string" value={formData.canonical_smiles} onChange={e => setFormData({ ...formData, canonical_smiles: e.target.value })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>MW (g/mol)</label>
                  <input type="number" step="0.1" value={formData.molecular_weight_g_mol} onChange={e => setFormData({ ...formData, molecular_weight_g_mol: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem' }}>Melting Point Tm (K)</label>
                  <input type="number" step="0.1" value={formData.tm_k} onChange={e => setFormData({ ...formData, tm_k: parseFloat(e.target.value) })} style={{ width: '100%', padding: '0.4rem', background: 'var(--bg)', color: '#fff', border: '1px solid var(--border)' }} />
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
                <button type="submit" className="btn" disabled={saving} style={{ flex: 1 }}>{saving ? 'Saving...' : 'Save Drug Profile'}</button>
                <button type="button" className="btn" onClick={() => setShowModal(false)} style={{ background: 'transparent', border: '1px solid var(--border)' }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
