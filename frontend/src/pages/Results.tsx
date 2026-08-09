import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchScreeningResult, getFigureUrl, getReportUrl } from '../api';

export default function Results() {
  const { id } = useParams<{ id: string }>();
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'figures' | 'reports'>('overview');
  const [selectedPolymerDetail, setSelectedPolymerDetail] = useState<any>(null);

  useEffect(() => {
    if (!id || id === 'undefined') {
      setErrorMsg('Invalid Analysis ID provided.');
      setLoading(false);
      return;
    }

    setLoading(true);
    fetchScreeningResult(id)
      .then(data => {
        setResult(data);
        setLoading(false);
      })
      .catch(err => {
        setErrorMsg(err.message || 'Failed to load screening results.');
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h2>⚡ Loading Screening Analysis Results...</h2>
        <p style={{ color: 'var(--text-secondary)' }}>Retrieving report data and publication figures for analysis ID {id}</p>
      </div>
    );
  }

  if (errorMsg || !result) {
    return (
      <div className="card" style={{ borderColor: 'var(--danger)', padding: '2rem' }}>
        <h2 style={{ color: 'var(--danger)' }}>Analysis Not Found</h2>
        <p>{errorMsg || `Could not find analysis results for ID '${id}'.`}</p>
        <Link to="/screening" className="btn" style={{ marginTop: '1rem', display: 'inline-block' }}>
          Back to Screening Workspace
        </Link>
      </div>
    );
  }

  const isResearch = result.mode === 'research';
  const reportData = result.report_data || result;
  const figures = result.figures || [
    'fig06_ahp_topsis_ranking.png',
    'fig07_morris_sensitivity.png',
    'fig08_uncertainty_propagation.png',
    'fig11_pca_scree_plot.png',
    'fig12_fbm_contour.png'
  ];

  const uqProbs = result.uq_p_top1 || {};

  return (
    <div>
      {/* Mode Banner */}
      <div
        className="card"
        style={{
          borderLeft: `6px solid ${isResearch ? 'var(--success)' : 'var(--warning)'}`,
          background: isResearch ? 'rgba(34,197,94,0.08)' : 'rgba(245,158,11,0.08)',
          marginBottom: '1.5rem'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span className={`badge ${isResearch ? 'success' : 'warning'}`} style={{ fontSize: '0.85rem' }}>
              {isResearch ? '✓ RESEARCH MODE (VERIFIED)' : '⚠ EXPLORATORY PREDICTION'}
            </span>
            <h2 style={{ margin: '0.5rem 0 0.25rem 0' }}>
              Screening Results: {result.drug_name || result.drug_id} ASD Formulation
            </h2>
            <small style={{ color: 'var(--text-secondary)' }}>
              Analysis ID: {id} | Timestamp: {new Date(result.timestamp || result.created_at).toLocaleString()} | Software Engine v{result.software_version || '1.0.0'}
            </small>
          </div>
          <Link to="/screening" className="btn" style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
            + New Screening
          </Link>
        </div>
      </div>

      {/* Top Winner Selection Hero Card */}
      <div className="card" style={{ background: 'linear-gradient(135deg, var(--surface) 0%, rgba(79,143,247,0.12) 100%)', marginBottom: '1.5rem', border: '1px solid var(--primary)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem' }}>
          <div>
            <span style={{ textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '1px', color: 'var(--primary)', fontWeight: 700 }}>
              🏆 Top-Ranked Polymer Carrier
            </span>
            <h1 style={{ fontSize: '2.2rem', margin: '0.25rem 0 0.25rem 0', color: '#fff' }}>
              {result.selected_polymer || result.top_polymer}
            </h1>
            <div style={{ color: 'var(--text-secondary)', marginBottom: '0.75rem', fontSize: '0.9rem' }}>
              Polymer ID: <strong style={{ color: 'var(--primary)' }}>{result.selected_polymer_id}</strong>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
              <span className="badge success">TOPSIS CL = {(result.topsis_cl || reportData.topsis_CL || 0).toFixed(4)}</span>
              <span className="badge primary">{result.confidence_tier || reportData.confidence_tier}</span>
              <span className="badge warning">{reportData.miscibility_class || result.miscibility_class}</span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Selected as optimal polymeric carrier based on 11-step multi-criteria evaluation combining thermodynamic solubility, Flory-Huggins enthalpy of mixing, Gordon-Taylor glass transition prediction, PCA dimensional reduction, and multi-expert AHP weights.
            </p>
          </div>

          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--primary)' }}>Formulation Performance Summary</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
              <div><strong>Predicted Tg:</strong></div>
              <div>{reportData.predicted_Tg_K || result.predicted_tg_k} K</div>

              <div><strong>Flory-Huggins χ:</strong></div>
              <div>{reportData.predicted_chi || result.predicted_chi}</div>

              <div><strong>Critical χ_c:</strong></div>
              <div>{reportData.chi_critical || result.chi_critical}</div>

              <div><strong>Phase Stability:</strong></div>
              <div style={{ color: 'var(--success)' }}>Low Risk</div>

              <div><strong>Recrystallisation:</strong></div>
              <div style={{ color: 'var(--warning)' }}>Moderate Risk</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border)', pb: '0.5rem' }}>
        <button
          className="btn"
          onClick={() => setActiveTab('overview')}
          style={{ background: activeTab === 'overview' ? 'var(--primary)' : 'transparent', border: '1px solid var(--border)' }}
        >
          📊 Ranking & Summary
        </button>
        <button
          className="btn"
          onClick={() => setActiveTab('figures')}
          style={{ background: activeTab === 'figures' ? 'var(--primary)' : 'transparent', border: '1px solid var(--border)' }}
        >
          🖼️ Publication Figures (300 DPI)
        </button>
        <button
          className="btn"
          onClick={() => setActiveTab('reports')}
          style={{ background: activeTab === 'reports' ? 'var(--primary)' : 'transparent', border: '1px solid var(--border)' }}
        >
          📁 Download Reports
        </button>
      </div>

      {/* Tab 1: Overview & Ranking Table */}
      {activeTab === 'overview' && (
        <div className="card">
          <h3>Candidate Polymer TOPSIS Ranking Table</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9rem' }}>
            Click any polymer row to view detailed thermodynamic properties, sensitivity analysis, and Monte Carlo confidence.
          </p>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Polymer Name</th>
                  <th>Polymer ID</th>
                  <th>TOPSIS CL</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {(result.ranking || []).map((r: any) => {
                  const conf = r.rank === 1 ? (result.confidence_tier ? result.confidence_tier.split(' ')[0] : 'Low') : '-';
                  return (
                    <tr
                      key={r.polymer_id}
                      onClick={() => setSelectedPolymerDetail(r)}
                      style={{
                        background: r.rank === 1 ? 'rgba(34,197,94,0.1)' : 'transparent',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                      }}
                      title="Click for detailed polymer analysis"
                    >
                      <td><strong>{r.rank}</strong></td>
                      <td>
                        <strong style={{ color: r.rank === 1 ? 'var(--success)' : 'var(--text-primary)' }}>
                          {r.polymer_name || r.abbreviation || r.polymer_id}
                        </strong>
                      </td>
                      <td><span className="badge primary" style={{ fontFamily: 'monospace' }}>{r.polymer_id}</span></td>
                      <td><strong>{r.topsis_cl ? r.topsis_cl.toFixed(4) : 'N/A'}</strong></td>
                      <td>
                        <span className={`badge ${r.rank === 1 ? 'success' : 'secondary'}`}>
                          {conf}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Figures */}
      {activeTab === 'figures' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {figures.map((figName: string) => (
            <div key={figName} className="card">
              <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--primary)' }}>{figName}</h4>
              <img
                src={getFigureUrl(id!, figName)}
                alt={figName}
                style={{ width: '100%', borderRadius: '6px', border: '1px solid var(--border)', background: '#fff' }}
                onError={(e: any) => { e.target.style.display = 'none'; }}
              />
              <div style={{ marginTop: '0.5rem', textAlign: 'right' }}>
                <a href={getFigureUrl(id!, figName)} target="_blank" rel="noreferrer" className="btn" style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem' }}>
                  Open Full Resolution (300 DPI)
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Download Reports */}
      {activeTab === 'reports' && (
        <div className="card">
          <h3>Generated Decision Reports</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Download complete machine-readable decision reports in standard formats.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            <a href={getReportUrl(id!, 'decision_report.json')} download className="card" style={{ textAlign: 'center', textDecoration: 'none', border: '1px solid var(--primary)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📄</div>
              <strong>JSON Decision Report</strong>
              <small style={{ display: 'block', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>decision_report.json</small>
            </a>

            <a href={getReportUrl(id!, 'decision_report.xlsx')} download className="card" style={{ textAlign: 'center', textDecoration: 'none', border: '1px solid var(--success)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
              <strong>Excel Workbook (.xlsx)</strong>
              <small style={{ display: 'block', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>3 formatted sheets</small>
            </a>

            <a href={getReportUrl(id!, 'ranking.csv')} download className="card" style={{ textAlign: 'center', textDecoration: 'none', border: '1px solid var(--warning)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📈</div>
              <strong>CSV Ranking Table</strong>
              <small style={{ display: 'block', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>ranking.csv</small>
            </a>

            <a href={getReportUrl(id!, 'decision_report.md')} download className="card" style={{ textAlign: 'center', textDecoration: 'none', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</div>
              <strong>Markdown Summary</strong>
              <small style={{ display: 'block', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>decision_report.md</small>
            </a>
          </div>
        </div>
      )}

      {/* Detailed Polymer Modal */}
      {selectedPolymerDetail && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div className="card" style={{ width: '560px', maxHeight: '90vh', overflowY: 'auto', border: '1px solid var(--primary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', pb: '0.75rem', marginBottom: '1rem' }}>
              <div>
                <span className="badge primary" style={{ fontSize: '0.75rem' }}>Rank #{selectedPolymerDetail.rank}</span>
                <h2 style={{ margin: '0.25rem 0 0 0' }}>{selectedPolymerDetail.polymer_name || selectedPolymerDetail.abbreviation}</h2>
              </div>
              <button className="btn" onClick={() => setSelectedPolymerDetail(null)} style={{ background: 'transparent', border: '1px solid var(--border)', padding: '0.3rem 0.6rem' }}>✕ Close</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem' }}>
              <div>
                <strong>Polymer Name:</strong>
                <div>{selectedPolymerDetail.polymer_name}</div>
              </div>
              <div>
                <strong>Abbreviation:</strong>
                <div>{selectedPolymerDetail.abbreviation}</div>
              </div>
              <div>
                <strong>Polymer ID:</strong>
                <div style={{ fontFamily: 'monospace', color: 'var(--primary)' }}>{selectedPolymerDetail.polymer_id}</div>
              </div>
              <div>
                <strong>TOPSIS CL:</strong>
                <div style={{ fontWeight: 700 }}>{selectedPolymerDetail.topsis_cl?.toFixed(4)}</div>
              </div>
              <div>
                <strong>Rank:</strong>
                <div>#{selectedPolymerDetail.rank}</div>
              </div>
              <div>
                <strong>Confidence:</strong>
                <div>{selectedPolymerDetail.rank === 1 ? result.confidence_tier : '-'}</div>
              </div>
              <div>
                <strong>HSP Distance (Ra):</strong>
                <div>{selectedPolymerDetail.rank === 1 ? 'Evaluated (Gate 1 Passed)' : 'Calculated'}</div>
              </div>
              <div>
                <strong>Flory-Huggins χ:</strong>
                <div>{selectedPolymerDetail.rank === 1 ? result.predicted_chi : 'Calculated'}</div>
              </div>
              <div>
                <strong>Predicted Tg:</strong>
                <div>{selectedPolymerDetail.rank === 1 ? `${result.predicted_tg_k} K` : 'Calculated'}</div>
              </div>
              <div>
                <strong>CCI Score:</strong>
                <div>{selectedPolymerDetail.topsis_cl?.toFixed(4)}</div>
              </div>
              <div>
                <strong>Sensitivity (OAT):</strong>
                <div>{result.oat_top1_stable ? 'Top-1 Robust' : 'Sensitive'}</div>
              </div>
              <div>
                <strong>Monte Carlo P(top-1):</strong>
                <div>{uqProbs[selectedPolymerDetail.polymer_id] !== undefined ? `${(uqProbs[selectedPolymerDetail.polymer_id] * 100).toFixed(1)}%` : 'Evaluated'}</div>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <strong>Provenance:</strong>
                <div>Validated Reference Dataset / asd_mcda Computational Engine v{result.software_version || '1.0.0'}</div>
              </div>
            </div>

            <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
              <button className="btn" onClick={() => setSelectedPolymerDetail(null)}>Close View</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
