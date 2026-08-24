import React from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';

interface GateIndicatorProps {
  passed: boolean;
  label: string;
}

const GateIndicator: React.FC<GateIndicatorProps> = ({ passed, label }) => {
  return (
    <div className={`gate-indicator ${passed ? 'gate-pass' : 'gate-fail'}`} style={{ display: 'flex', alignItems: 'center', gap: '4px', color: passed ? 'var(--color-success)' : 'var(--color-error)' }}>
      {passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
      <span className="gate-label">{label}</span>
    </div>
  );
};

export default GateIndicator;
