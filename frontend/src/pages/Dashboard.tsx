import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Play, Pill, FlaskConical, Clock, CheckCircle2, FileText, ArrowRight } from 'lucide-react';
import { fetchHistory, fetchVersion } from '../api';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, EmptyState, LoadingState } from '../components/ui';

const Dashboard: React.FC<{ version?: any }> = ({ version: propVersion }) => {
  const [recentAnalyses, setRecentAnalyses] = useState<any[]>([]);
  const [engineVersion, setEngineVersion] = useState<string>(propVersion?.engine_version || 'v1.5.0-FOUR-CRITERION-FREEZE');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      setIsLoading(true);
      try {
        const [historyData, versionData] = await Promise.all([
          fetchHistory().catch(() => []),
          fetchVersion().catch(() => null)
        ]);
        if (!isMounted) return;
        if (Array.isArray(historyData)) {
          setRecentAnalyses(historyData.slice(0, 5));
        }
        if (versionData && versionData.engine_version) {
          setEngineVersion(versionData.engine_version);
        }
      } catch (err: any) {
        if (!isMounted) return;
        console.error('Failed to load dashboard data:', err);
        setError(err?.message || 'Failed to load recent analyses.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    loadData();
    return () => { isMounted = false; };
  }, []);

  return (
    <div className="page-container">
      <header className="header" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <img src="/logo-symbol.svg" alt="PharmaPolySCOPE Logo" style={{ width: '42px', height: '42px' }} />
          <div>
            <h1 className="title" style={{ margin: 0, letterSpacing: '-0.02em' }}>
              PharmaPoly<span style={{ fontWeight: 700, color: 'var(--color-primary-action)' }}>SCOPE</span>
            </h1>
            <p style={{ color: 'var(--color-secondary-text)', margin: '0.2rem 0 0 0', fontSize: '13px' }}>
              Pharmaceutical Polymer Screening and Computational Optimization Platform
            </p>
          </div>
        </div>
      </header>

      {/* Project Status Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', backgroundColor: 'var(--color-surface)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--color-muted-text)', fontWeight: 600, display: 'block' }}>
                Scientific Baseline Freeze
              </span>
              <div className="text-mono" style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-primary-action)' }}>
                {engineVersion || 'v1.5.0-FOUR-CRITERION-FREEZE'}
              </div>
            </div>
            <div style={{ width: '1px', height: '28px', backgroundColor: 'var(--color-border)' }}></div>
            <div>
              <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--color-muted-text)', fontWeight: 600, display: 'block' }}>
                Engine Status
              </span>
              <div style={{ fontSize: '13px', color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
                <CheckCircle2 size={14} /> Online / Operational
              </div>
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--color-muted-text)', fontWeight: 600, display: 'block', textAlign: 'right' }}>
              Methodology
            </span>
            <div style={{ fontSize: '13px', color: 'var(--color-secondary-text)' }}>
              HSP + Flory-Huggins + Gordon-Taylor + PCA-AHP-TOPSIS + Monte Carlo UQ
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <Link to="/screening" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ height: '100%', cursor: 'pointer', transition: 'all 0.2s', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '0.5rem', padding: '0.5rem 0' }}>
              <div style={{ padding: '0.75rem', backgroundColor: 'var(--color-info-bg)', color: 'var(--color-primary-action)', borderRadius: '50%' }}>
                <Play size={22} />
              </div>
              <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--color-primary-text)' }}>Computational Screening</h3>
              <small style={{ color: 'var(--color-muted-text)' }}>Run 11-step candidate screening</small>
            </div>
          </div>
        </Link>

        <Link to="/drugs" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ height: '100%', cursor: 'pointer', transition: 'all 0.2s', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '0.5rem', padding: '0.5rem 0' }}>
              <div style={{ padding: '0.75rem', backgroundColor: '#EDE9FE', color: '#7C3AED', borderRadius: '50%' }}>
                <Pill size={22} />
              </div>
              <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--color-primary-text)' }}>Drug API Library</h3>
              <small style={{ color: 'var(--color-muted-text)' }}>View physicochemical profiles</small>
            </div>
          </div>
        </Link>

        <Link to="/polymers" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ height: '100%', cursor: 'pointer', transition: 'all 0.2s', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '0.5rem', padding: '0.5rem 0' }}>
              <div style={{ padding: '0.75rem', backgroundColor: 'var(--color-success-bg)', color: 'var(--color-success)', borderRadius: '50%' }}>
                <FlaskConical size={22} />
              </div>
              <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--color-primary-text)' }}>Polymer Carriers</h3>
              <small style={{ color: 'var(--color-muted-text)' }}>Explore excipient database</small>
            </div>
          </div>
        </Link>

        <Link to="/history" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ height: '100%', cursor: 'pointer', transition: 'all 0.2s', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '0.5rem', padding: '0.5rem 0' }}>
              <div style={{ padding: '0.75rem', backgroundColor: 'var(--color-warning-bg)', color: 'var(--color-warning)', borderRadius: '50%' }}>
                <Clock size={22} />
              </div>
              <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--color-primary-text)' }}>Audit History</h3>
              <small style={{ color: 'var(--color-muted-text)' }}>Historical run provenance</small>
            </div>
          </div>
        </Link>
      </div>

      {/* Methodology Overview */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-primary-text)', marginBottom: '0.75rem' }}>
          Methodology & Theoretical Framework Status
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div className="card" style={{ margin: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--color-info)' }}>
              <FlaskConical size={16} />
              <strong style={{ fontSize: '13px' }}>Thermodynamic Miscibility</strong>
            </div>
            <ul style={{ fontSize: '12px', color: 'var(--color-secondary-text)', paddingLeft: '1.2rem', lineHeight: '1.6' }}>
              <li>Hansen Solubility Distances (Ra, RED)</li>
              <li>Flory-Huggins Interaction (χ, χc)</li>
            </ul>
          </div>

          <div className="card" style={{ margin: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--color-warning)' }}>
              <Play size={16} />
              <strong style={{ fontSize: '13px' }}>Glass Dynamics</strong>
            </div>
            <ul style={{ fontSize: '12px', color: 'var(--color-secondary-text)', paddingLeft: '1.2rem', lineHeight: '1.6' }}>
              <li>Gordon-Taylor Tg,mix Prediction</li>
              <li>Simha-Boyer Constant K</li>
            </ul>
          </div>

          <div className="card" style={{ margin: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--color-success)' }}>
              <CheckCircle2 size={16} />
              <strong style={{ fontSize: '13px' }}>Multi-Criteria Decision Analysis</strong>
            </div>
            <ul style={{ fontSize: '12px', color: 'var(--color-secondary-text)', paddingLeft: '1.2rem', lineHeight: '1.6' }}>
              <li>PCA Dimensionality Reduction</li>
              <li>AHP Expert Weighting (CR = 0.0000)</li>
              <li>TOPSIS Closeness Ranking (CL)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-primary-text)', margin: 0 }}>
            Recent Screening Analyses
          </h2>
          <Link to="/history" style={{ fontSize: '13px', color: 'var(--color-primary-action)', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}>
            View All <ArrowRight size={14} />
          </Link>
        </div>

        {isLoading ? (
          <LoadingState message="Loading recent analyses..." rows={3} />
        ) : error ? (
          <div className="error-banner">{error}</div>
        ) : recentAnalyses.length === 0 ? (
          <EmptyState 
            icon={<FileText size={40} className="text-muted" />}
            title="No Analyses Found"
            description="No computational screening runs found in local history."
            action={
              <Link to="/screening">
                <Button variant="primary">Start First Screening</Button>
              </Link>
            }
          />
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ANALYSIS ID</th>
                  <th>DATE / TIME</th>
                  <th>DRUG API</th>
                  <th>CANDIDATES</th>
                  <th>TOP SELECTION</th>
                  <th className="numeric">TOPSIS CL</th>
                  <th>CONFIDENCE</th>
                  <th style={{ textAlign: 'right' }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.map((analysis) => {
                  const aId = analysis.analysis_id || analysis.id || 'N/A';
                  const rawDate = analysis.timestamp || analysis.created_at;
                  const dateStr = rawDate ? new Date(rawDate).toLocaleString() : 'N/A';
                  const drugLabel = analysis.drug_name || analysis.drug_id || 'N/A';
                  const polyCount = analysis.polymer_ids ? analysis.polymer_ids.length : (analysis.candidates_count || 0);
                  const topPol = analysis.top_polymer || analysis.top_selection || 'N/A';
                  const clVal = typeof analysis.topsis_cl === 'number' ? analysis.topsis_cl.toFixed(4) : 'N/A';
                  const conf = analysis.confidence_tier || analysis.confidence || 'N/A';

                  return (
                    <tr key={aId}>
                      <td className="mono" style={{ fontSize: '12px', fontWeight: 600 }}>
                        {aId.length > 16 ? `${aId.substring(0, 16)}...` : aId}
                      </td>
                      <td style={{ fontSize: '12px' }}>{dateStr}</td>
                      <td><strong>{drugLabel}</strong></td>
                      <td>{polyCount} polymers</td>
                      <td><strong style={{ color: 'var(--color-primary-action)' }}>{topPol}</strong></td>
                      <td className="numeric">{clVal}</td>
                      <td>
                        <Badge variant={conf.toLowerCase().includes('high') ? 'success' : conf.toLowerCase().includes('mod') || conf.toLowerCase().includes('med') ? 'warning' : 'primary'}>
                          {conf}
                        </Badge>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <Link to={`/results/${aId}`}>
                          <Button variant="secondary" size="sm">View Results</Button>
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
