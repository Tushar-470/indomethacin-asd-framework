import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, Trash2, AlertTriangle, FileText } from 'lucide-react';
import { fetchHistory, deleteHistory } from '../api';
import { Button, Badge, EmptyState, LoadingState } from '../components/ui';

const History: React.FC = () => {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchHistory();
      if (Array.isArray(data)) {
        setAnalyses(data);
      } else {
        setAnalyses([]);
      }
    } catch (err: any) {
      console.error('Failed to load history:', err);
      setError(err?.message || 'Failed to retrieve analysis history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm(`Are you sure you want to delete analysis record '${id}'? This cannot be undone.`)) {
      return;
    }
    
    setIsDeleting(id);
    try {
      await deleteHistory(id);
      setAnalyses(prev => prev.filter(a => (a.analysis_id || a.id) !== id));
    } catch (err: any) {
      console.error('Failed to delete record:', err);
      alert(err?.message || 'Failed to delete the analysis record.');
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <div className="page-container">
      <header className="header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Clock size={24} style={{ color: 'var(--color-primary-action)' }} />
            <h1 className="title" style={{ margin: 0 }}>Analysis Audit Trail & Provenance History</h1>
          </div>
          <p style={{ color: 'var(--color-secondary-text)', margin: 0 }}>
            Chronological record of all computational screening runs and decision reports
          </p>
        </div>
      </header>

      {error && (
        <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={18} style={{ flexShrink: 0 }} />
          <div>
            <strong>Error Loading History:</strong> {error}
            <div style={{ marginTop: '0.5rem' }}>
              <Button variant="secondary" size="sm" onClick={loadHistory}>Retry</Button>
            </div>
          </div>
        </div>
      )}

      {!error && isLoading ? (
        <LoadingState message="Loading audit trail..." rows={5} />
      ) : !error && analyses.length === 0 ? (
        <EmptyState 
          icon={<FileText size={48} className="text-muted" />}
          title="No History Found"
          description="There are no computational screening records in the database."
          action={
            <Link to="/screening">
              <Button variant="primary">Start New Screening</Button>
            </Link>
          }
        />
      ) : !error && (
        <div className="card">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ANALYSIS ID</th>
                  <th>DATE / TIME</th>
                  <th>DRUG API</th>
                  <th>CANDIDATES</th>
                  <th>MODE</th>
                  <th>TOP SELECTION</th>
                  <th className="numeric">TOPSIS CL</th>
                  <th>CONFIDENCE</th>
                  <th style={{ textAlign: 'right' }}>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map((analysis) => {
                  const aId = analysis.analysis_id || analysis.id || 'N/A';
                  const rawDate = analysis.timestamp || analysis.created_at;
                  const dateStr = rawDate ? new Date(rawDate).toLocaleString() : 'N/A';
                  const drugLabel = analysis.drug_name || analysis.drug_id || 'N/A';
                  const polyCount = analysis.polymer_ids ? analysis.polymer_ids.length : (analysis.candidates_count || 0);
                  const modeStr = (analysis.mode || 'exploratory').toUpperCase();
                  const isResearch = modeStr.toLowerCase() === 'research';
                  const topPol = analysis.top_polymer || analysis.top_selection || 'N/A';
                  const clVal = typeof analysis.topsis_cl === 'number' ? analysis.topsis_cl.toFixed(4) : 'N/A';
                  const conf = analysis.confidence_tier || analysis.confidence || 'N/A';

                  return (
                    <tr key={aId}>
                      <td className="mono" style={{ fontSize: '12px', fontWeight: 600 }}>{aId}</td>
                      <td style={{ fontSize: '12px', whiteSpace: 'nowrap' }}>{dateStr}</td>
                      <td><strong>{drugLabel}</strong></td>
                      <td>{polyCount} screened</td>
                      <td>
                        <Badge variant={isResearch ? 'success' : 'warning'}>
                          {modeStr}
                        </Badge>
                      </td>
                      <td><strong style={{ color: 'var(--color-primary-action)' }}>{topPol}</strong></td>
                      <td className="numeric">{clVal}</td>
                      <td>
                        <Badge variant={conf.toLowerCase().includes('high') ? 'success' : conf.toLowerCase().includes('mod') || conf.toLowerCase().includes('med') ? 'warning' : 'primary'}>
                          {conf}
                        </Badge>
                      </td>
                      <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                          <Link to={`/results/${aId}`}>
                            <Button variant="secondary" size="sm">View</Button>
                          </Link>
                          <Button 
                            variant="danger" 
                            size="sm" 
                            disabled={isDeleting === aId}
                            onClick={() => handleDelete(aId)}
                            title="Delete record"
                          >
                            {isDeleting === aId ? '...' : <Trash2 size={13} />}
                          </Button>
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
    </div>
  );
};

export default History;
