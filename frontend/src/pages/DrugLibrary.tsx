import React, { useEffect, useState, useRef } from 'react';
import { Button, Badge, Modal, Drawer, EmptyState, LoadingState } from '../components/ui';
import { ScientificValue } from '../components/scientific';
import { Plus, Search, Eye, Trash2, Pill, AlertTriangle, SlidersHorizontal } from 'lucide-react';
import { fetchDrugs, createDrug, deleteDrug } from '../api';

export default function DrugLibrary() {
  const [drugs, setDrugs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedDrugDetail, setSelectedDrugDetail] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [saving, setSaving] = useState(false);

  // Column visibility state (Pure scientific parameters)
  const [visibleColumns, setVisibleColumns] = useState({
    mw: true,
    tm: true,
    tg: true,
    density: true,
    hsp: true,
    r0: true,
    bcs: true,
  });
  const [showColumnMenu, setShowColumnMenu] = useState(false);
  const columnMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (columnMenuRef.current && !columnMenuRef.current.contains(event.target as Node)) {
        setShowColumnMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Form state for add modal
  const [formData, setFormData] = useState({
    drug_id: '',
    generic_name: '',
    canonical_smiles: '',
    molecular_weight_g_mol: 357.79,
    tm_k: 433.15,
    tg_k: 315.15,
    density_crystalline_g_cm3: 1.31,
    density_amorphous_g_cm3: 1.22,
    density_source: 'literature',
    bcs_class: 'II',
    logp: 4.27,
    hbd: 2,
    hba: 4,
    tpsa_angstrom2: 68.5,
    hsp_delta_d: 19.2,
    hsp_delta_p: 7.9,
    hsp_delta_h: 8.4,
    hsp_ro: 8.0,
    hsp_source: 'literature',
    molar_volume_cm3_mol: 273.0,
    reference_doi: '',
    reference_source: 'user_entered',
    validation_status: 'draft'
  });

  const loadDrugs = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await fetchDrugs();
      setDrugs(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to load drug profiles.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDrugs();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    // Comprehensive client-side validation
    if (!formData.drug_id?.trim()) {
      setErrorMsg('Drug ID is required.');
      return;
    }
    if (!formData.generic_name?.trim()) {
      setErrorMsg('Generic Name is required.');
      return;
    }
    if (!formData.canonical_smiles?.trim()) {
      setErrorMsg('Canonical SMILES is required.');
      return;
    }

    const mw = Number(formData.molecular_weight_g_mol);
    if (isNaN(mw) || mw <= 0) {
      setErrorMsg('Molecular Weight must be a valid positive number (> 0 g/mol).');
      return;
    }

    const tm = Number(formData.tm_k);
    if (isNaN(tm) || tm <= 0) {
      setErrorMsg('Melting Point Tm must be a valid positive number (K).');
      return;
    }

    const dens = Number(formData.density_crystalline_g_cm3);
    if (isNaN(dens) || dens <= 0) {
      setErrorMsg('Crystalline Density is required and must be a valid positive number (g/cm³).');
      return;
    }

    const dD = Number(formData.hsp_delta_d);
    const dP = Number(formData.hsp_delta_p);
    const dH = Number(formData.hsp_delta_h);
    const r0 = Number(formData.hsp_ro);
    if (isNaN(dD) || dD < 0 || isNaN(dP) || dP < 0 || isNaN(dH) || dH < 0) {
      setErrorMsg('Hansen solubility parameters (δD, δP, δH) must be valid non-negative numbers.');
      return;
    }
    if (isNaN(r0) || r0 <= 0) {
      setErrorMsg('HSP Interaction Radius R₀ must be a valid positive number (> 0 MPa½).');
      return;
    }

    if (formData.tg_k) {
      const tg = Number(formData.tg_k);
      if (isNaN(tg) || tg <= 0) {
        setErrorMsg('Glass Transition Tg must be a valid positive number (K).');
        return;
      }
      if (tg >= tm) {
        setErrorMsg(`Glass Transition Tg (${tg} K) cannot be greater than or equal to Melting Point Tm (${tm} K).`);
        return;
      }
    }

    setSaving(true);
    try {
      await createDrug({
        ...formData,
        drug_id: formData.drug_id.trim(),
        generic_name: formData.generic_name.trim(),
        canonical_smiles: formData.canonical_smiles.trim(),
        molecular_weight_g_mol: mw,
        tm_k: tm,
        tg_k: formData.tg_k ? Number(formData.tg_k) : undefined,
        density_crystalline_g_cm3: dens,
        density_amorphous_g_cm3: formData.density_amorphous_g_cm3 ? Number(formData.density_amorphous_g_cm3) : undefined,
        hsp_delta_d: dD,
        hsp_delta_p: dP,
        hsp_delta_h: dH,
        hsp_ro: r0,
        molar_volume_cm3_mol: Number(formData.molar_volume_cm3_mol) || Math.round((mw / dens) * 10) / 10,
        logp: formData.logp !== undefined ? Number(formData.logp) : undefined,
        hbd: formData.hbd !== undefined ? Number(formData.hbd) : undefined,
        hba: formData.hba !== undefined ? Number(formData.hba) : undefined,
        tpsa_angstrom2: formData.tpsa_angstrom2 !== undefined ? Number(formData.tpsa_angstrom2) : undefined,
        bcs_class: formData.bcs_class || 'II'
      });
      setShowAddModal(false);
      loadDrugs();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create drug profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(`Delete user drug profile '${id}'? This cannot be undone.`)) return;
    try {
      await deleteDrug(id);
      loadDrugs();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to delete drug profile.');
    }
  };

  const filteredDrugs = drugs.filter(d => {
    const id = d.drug_id || d.id || '';
    const name = d.generic_name || d.genericName || '';
    return id.toLowerCase().includes(searchTerm.toLowerCase()) || 
           name.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="page-container">
      <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Pill size={24} style={{ color: 'var(--color-primary-action)' }} />
            <h1 className="title" style={{ margin: 0 }}>Drug Profile Library</h1>
          </div>
          <p style={{ color: 'var(--color-secondary-text)', margin: 0 }}>
            Active Pharmaceutical Ingredients (APIs) and physicochemical properties for solid dispersion screening
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Column Visibility Control */}
          <div className="column-visibility-dropdown" ref={columnMenuRef}>
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={() => setShowColumnMenu(!showColumnMenu)}
              icon={<SlidersHorizontal size={13} />}
            >
              Columns
            </Button>
            {showColumnMenu && (
              <div className="dropdown-menu">
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-muted-text)', textTransform: 'uppercase', marginBottom: '6px', padding: '2px 6px' }}>
                  Toggle Columns
                </div>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.mw} onChange={e => setVisibleColumns({ ...visibleColumns, mw: e.target.checked })} />
                  <span>Molecular Weight</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.tm} onChange={e => setVisibleColumns({ ...visibleColumns, tm: e.target.checked })} />
                  <span>Melting Point Tm</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.tg} onChange={e => setVisibleColumns({ ...visibleColumns, tg: e.target.checked })} />
                  <span>Glass Transition Tg</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.density} onChange={e => setVisibleColumns({ ...visibleColumns, density: e.target.checked })} />
                  <span>Crystalline Density</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.hsp} onChange={e => setVisibleColumns({ ...visibleColumns, hsp: e.target.checked })} />
                  <span>HSP (δD / δP / δH)</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.r0} onChange={e => setVisibleColumns({ ...visibleColumns, r0: e.target.checked })} />
                  <span>Interaction Radius R₀</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.bcs} onChange={e => setVisibleColumns({ ...visibleColumns, bcs: e.target.checked })} />
                  <span>BCS Class</span>
                </label>
              </div>
            )}
          </div>

          <Button onClick={() => setShowAddModal(true)} icon={<Plus size={16} />}>
            Add Drug Profile
          </Button>
        </div>
      </div>

      <div className="card" style={{ padding: '0.75rem 1rem', marginBottom: '1.5rem' }}>
        <div style={{ position: 'relative', maxWidth: '400px' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-muted-text)' }} />
          <input 
            type="text" 
            placeholder="Filter by ID or generic name..." 
            style={{ paddingLeft: '32px', height: '36px' }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {errorMsg && (
        <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <LoadingState message="Loading drug library..." rows={4} />
      ) : filteredDrugs.length === 0 ? (
        <EmptyState title="No drugs found" description="Try adjusting your search or add a new drug profile." />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th className="sticky-col-1">DRUG ID</th>
                  <th className="sticky-col-2">GENERIC NAME</th>
                  {visibleColumns.mw && <th className="numeric">MW (G/MOL)</th>}
                  {visibleColumns.tm && <th className="numeric">TM (K)</th>}
                  {visibleColumns.tg && <th className="numeric">TG (K)</th>}
                  {visibleColumns.density && <th className="numeric">DENSITY (G/CM³)</th>}
                  {visibleColumns.hsp && <th className="numeric">HSP (δD / δP / δH)</th>}
                  {visibleColumns.r0 && <th className="numeric">R₀ (MPA½)</th>}
                  {visibleColumns.bcs && <th style={{ textAlign: 'center' }}>BCS</th>}
                  <th style={{ textAlign: 'right' }}>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {filteredDrugs.map(drug => {
                  const dId = drug.drug_id || drug.id;
                  const dName = drug.generic_name || drug.genericName;
                  const mw = drug.molecular_weight_g_mol ?? drug.mw;
                  const tm = drug.tm_k ?? drug.tm;
                  const tg = drug.tg_k ?? drug.tg ?? drug.tg_k_estimated;
                  const densityVal = drug.density_crystalline_g_cm3 ?? drug.density;
                  const dD = drug.hsp_delta_d ?? drug.hspD ?? 0;
                  const dP = drug.hsp_delta_p ?? drug.hspP ?? 0;
                  const dH = drug.hsp_delta_h ?? drug.hspH ?? 0;
                  const r0 = drug.hsp_ro ?? drug.r0 ?? 8.0;
                  const bcs = drug.bcs_class || drug.bcsClass || 'II';
                  const isRef = drug.is_reference ?? (drug.status === 'Reference');

                  return (
                    <tr key={dId}>
                      <td className="mono sticky-col-1" style={{ fontWeight: 600 }}>{dId}</td>
                      <td className="sticky-col-2"><strong>{dName}</strong></td>
                      {visibleColumns.mw && <td className="numeric">{typeof mw === 'number' ? mw.toFixed(2) : mw}</td>}
                      {visibleColumns.tm && <td className="numeric">{typeof tm === 'number' ? tm.toFixed(1) : tm}</td>}
                      {visibleColumns.tg && <td className="numeric">{typeof tg === 'number' ? tg.toFixed(1) : (tg || '-')}</td>}
                      {visibleColumns.density && <td className="numeric">{typeof densityVal === 'number' ? densityVal.toFixed(2) : densityVal}</td>}
                      {visibleColumns.hsp && <td className="numeric">{dD.toFixed(1)} / {dP.toFixed(1)} / {dH.toFixed(1)}</td>}
                      {visibleColumns.r0 && <td className="numeric">{typeof r0 === 'number' ? r0.toFixed(1) : r0}</td>}
                      {visibleColumns.bcs && <td style={{ textAlign: 'center' }}><span className="mono" style={{ fontWeight: 600 }}>Class {bcs}</span></td>}
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                          <Button variant="secondary" size="sm" onClick={() => setSelectedDrugDetail(drug)}>
                            View
                          </Button>
                          {!isRef && (
                            <Button variant="danger" size="sm" onClick={() => handleDelete(dId)}>
                              <Trash2 size={13} />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Drug Detail Drawer */}
      <Drawer 
        isOpen={!!selectedDrugDetail} 
        onClose={() => setSelectedDrugDetail(null)}
        title={selectedDrugDetail?.generic_name || selectedDrugDetail?.genericName || 'Drug Profile'}
        width={480}
      >
        {selectedDrugDetail && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span className="mono" style={{ fontWeight: 600, color: 'var(--color-primary-action)' }}>
                {selectedDrugDetail.drug_id || selectedDrugDetail.id}
              </span>
            </div>

            <div className="form-section">
              <div className="form-section-title">Identity & Structure</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '13px' }}>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>GENERIC NAME</span><strong>{selectedDrugDetail.generic_name}</strong></div>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>BCS CLASS</span><strong>Class {selectedDrugDetail.bcs_class || 'II'}</strong></div>
                <div style={{ gridColumn: 'span 2' }}>
                  <span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>CANONICAL SMILES</span>
                  <div className="mono" style={{ fontSize: '11px', background: 'var(--color-surface-subtle)', padding: '6px', borderRadius: '4px', wordBreak: 'break-all' }}>
                    {selectedDrugDetail.canonical_smiles || 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Thermophysical Parameters</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <ScientificValue label="Molecular Weight" value={selectedDrugDetail.molecular_weight_g_mol} unit="g/mol" precision={2} />
                <ScientificValue label="Melting Point Tm" value={selectedDrugDetail.tm_k} unit="K" precision={1} />
                <ScientificValue label="Glass Transition Tg" value={selectedDrugDetail.tg_k || selectedDrugDetail.tg_k_estimated} unit="K" precision={1} />
                <ScientificValue label="Crystalline Density" value={selectedDrugDetail.density_crystalline_g_cm3} unit="g/cm³" precision={2} />
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Solubility & Hansen Parameters</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <ScientificValue label="Dispersion (δD)" value={selectedDrugDetail.hsp_delta_d} unit="MPa½" precision={1} />
                <ScientificValue label="Polar (δP)" value={selectedDrugDetail.hsp_delta_p} unit="MPa½" precision={1} />
                <ScientificValue label="H-Bonding (δH)" value={selectedDrugDetail.hsp_delta_h} unit="MPa½" precision={1} />
                <ScientificValue label="Interaction Radius R₀" value={selectedDrugDetail.hsp_ro} unit="MPa½" precision={1} />
                <ScientificValue label="Molar Volume" value={selectedDrugDetail.molar_volume_cm3_mol} unit="cm³/mol" precision={1} />
              </div>
            </div>

            {(selectedDrugDetail.logp !== undefined || selectedDrugDetail.hbd !== undefined || selectedDrugDetail.tpsa_angstrom2 !== undefined) && (
              <div className="form-section" style={{ borderBottom: 'none' }}>
                <div className="form-section-title">Molecular Descriptors</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <ScientificValue label="LogP" value={selectedDrugDetail.logp} precision={2} />
                  <ScientificValue label="TPSA" value={selectedDrugDetail.tpsa_angstrom2} unit="Å²" precision={1} />
                  <ScientificValue label="H-Bond Donors" value={selectedDrugDetail.hbd} precision={0} />
                  <ScientificValue label="H-Bond Acceptors" value={selectedDrugDetail.hba} precision={0} />
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>

      {/* Add Drug Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add New Drug Profile" size="wide">
        <form onSubmit={handleSave}>
          <div className="form-section">
            <div className="form-section-title">1. Drug Identity</div>
            <div className="form-grid form-grid-2">
              <div className="form-group">
                <label className="form-label">Drug ID <span className="required">*</span></label>
                <input required type="text" placeholder="e.g. NAP-001-2026" value={formData.drug_id} onChange={e => setFormData({ ...formData, drug_id: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Generic Name <span className="required">*</span></label>
                <input required type="text" placeholder="e.g. Naproxen" value={formData.generic_name} onChange={e => setFormData({ ...formData, generic_name: e.target.value })} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="form-label">Canonical SMILES <span className="required">*</span></label>
                <input required type="text" placeholder="SMILES string" value={formData.canonical_smiles} onChange={e => setFormData({ ...formData, canonical_smiles: e.target.value })} />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">2. Molecular / Thermophysical Properties</div>
            <div className="form-grid form-grid-2">
              <div className="form-group">
                <label className="form-label">Molecular Weight MW <span className="unit">(g/mol)</span> <span className="required">*</span></label>
                <input required type="number" step="0.01" min="1" placeholder="e.g. 357.79" value={formData.molecular_weight_g_mol} onChange={e => setFormData({ ...formData, molecular_weight_g_mol: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">Melting Point Tm <span className="unit">(K)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="1" placeholder="e.g. 433.15" value={formData.tm_k} onChange={e => setFormData({ ...formData, tm_k: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">Glass Transition Tg <span className="unit">(K)</span></label>
                <input type="number" step="0.1" min="1" placeholder="Optional (estimates 0.70·Tm if blank)" value={formData.tg_k} onChange={e => setFormData({ ...formData, tg_k: e.target.value ? parseFloat(e.target.value) : undefined as any })} />
              </div>
              <div className="form-group">
                <label className="form-label">Crystalline Density <span className="unit">(g/cm³)</span> <span className="required">*</span></label>
                <input required type="number" step="0.01" min="0.01" placeholder="e.g. 1.31" value={formData.density_crystalline_g_cm3} onChange={e => setFormData({ ...formData, density_crystalline_g_cm3: parseFloat(e.target.value) })} />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">3. Hansen Solubility Parameters (HSP)</div>
            <div className="form-grid form-grid-2">
              <div className="form-group">
                <label className="form-label">δD <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0" placeholder="e.g. 19.2" value={formData.hsp_delta_d} onChange={e => setFormData({ ...formData, hsp_delta_d: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">δP <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0" placeholder="e.g. 7.9" value={formData.hsp_delta_p} onChange={e => setFormData({ ...formData, hsp_delta_p: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">δH <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0" placeholder="e.g. 8.4" value={formData.hsp_delta_h} onChange={e => setFormData({ ...formData, hsp_delta_h: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">Interaction Radius R₀ <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0.1" placeholder="e.g. 8.0" value={formData.hsp_ro} onChange={e => setFormData({ ...formData, hsp_ro: parseFloat(e.target.value) })} />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">4. Molecular Descriptors & Classification</div>
            <div className="form-grid form-grid-3">
              <div className="form-group">
                <label className="form-label">BCS Class</label>
                <select value={formData.bcs_class} onChange={e => setFormData({ ...formData, bcs_class: e.target.value })}>
                  <option value="I">Class I (High Sol, High Perm)</option>
                  <option value="II">Class II (Low Sol, High Perm)</option>
                  <option value="III">Class III (High Sol, Low Perm)</option>
                  <option value="IV">Class IV (Low Sol, Low Perm)</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">LogP</label>
                <input type="number" step="0.01" placeholder="e.g. 4.27" value={formData.logp} onChange={e => setFormData({ ...formData, logp: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">TPSA <span className="unit">(Å²)</span></label>
                <input type="number" step="0.1" min="0" placeholder="e.g. 68.5" value={formData.tpsa_angstrom2} onChange={e => setFormData({ ...formData, tpsa_angstrom2: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">H-Bond Donors (HBD)</label>
                <input type="number" min="0" step="1" placeholder="e.g. 2" value={formData.hbd} onChange={e => setFormData({ ...formData, hbd: parseInt(e.target.value, 10) })} />
              </div>
              <div className="form-group">
                <label className="form-label">H-Bond Acceptors (HBA)</label>
                <input type="number" min="0" step="1" placeholder="e.g. 4" value={formData.hba} onChange={e => setFormData({ ...formData, hba: parseInt(e.target.value, 10) })} />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <Button variant="secondary" type="button" onClick={() => setShowAddModal(false)}>Cancel</Button>
            <Button variant="primary" type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save Drug Profile'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
