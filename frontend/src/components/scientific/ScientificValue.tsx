import React from 'react';
import ProvenanceBadge, { ProvenanceType } from './ProvenanceBadge';

export interface ScientificValueProps {
  value: number | string | null | undefined;
  label?: string;
  unit?: string;
  precision?: number;
  provenance?: ProvenanceType;
  formatter?: (v: any) => string;
}

const ScientificValue: React.FC<ScientificValueProps> = ({
  value,
  label,
  unit,
  precision = 4,
  provenance,
  formatter
}) => {
  let formattedValue: string;
  if (value === null || value === undefined) {
    formattedValue = 'N/A';
  } else if (formatter) {
    formattedValue = formatter(value);
  } else if (typeof value === 'number') {
    formattedValue = Number.isInteger(value) ? String(value) : value.toFixed(precision);
  } else {
    formattedValue = String(value);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
      {label && <span style={{ fontSize: '11px', color: 'var(--color-muted-text)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</span>}
      <span className="scientific-value">
        <span className="value text-numeric">{formattedValue}</span>
        {unit && <span className="unit">{unit}</span>}
        {provenance && <ProvenanceBadge type={provenance} showLabel={false} />}
      </span>
    </div>
  );
};

export default ScientificValue;
