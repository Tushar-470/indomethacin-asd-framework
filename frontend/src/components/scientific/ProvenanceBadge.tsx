import React from 'react';

export type ProvenanceType = 'experimental' | 'calculated' | 'literature' | 'predicted' | 'assumption' | 'reference' | 'draft' | 'archived';

interface ProvenanceBadgeProps {
  type: ProvenanceType;
  showLabel?: boolean;
}

const typeMap: Record<ProvenanceType, { class: string; label: string }> = {
  experimental: { class: 'provenance-experimental', label: 'Experimental' },
  reference: { class: 'provenance-reference', label: 'Reference (Validated)' },
  calculated: { class: 'provenance-calculated', label: 'Calculated' },
  literature: { class: 'provenance-literature', label: 'Literature' },
  predicted: { class: 'provenance-predicted', label: 'Model-derived' },
  assumption: { class: 'provenance-assumption', label: 'Assumption' },
  draft: { class: 'provenance-draft', label: 'Draft' },
  archived: { class: 'provenance-archived', label: 'Historical' },
};

export const getProvenanceType = (item: { is_reference?: boolean; validation_status?: string; hsp_source?: string; reference_source?: string }): ProvenanceType => {
  if (item.is_reference) return 'reference';
  if (item.validation_status === 'draft') return 'draft';
  if (item.hsp_source === 'experimental' || item.reference_source === 'experimental') return 'experimental';
  if (item.hsp_source === 'literature' || item.reference_source === 'literature') return 'literature';
  if (item.hsp_source === 'calculated' || item.reference_source === 'calculated') return 'calculated';
  if (item.hsp_source === 'predicted' || item.reference_source === 'predicted') return 'predicted';
  if (item.validation_status === 'archived') return 'archived';
  return 'assumption';
};

const ProvenanceBadge: React.FC<ProvenanceBadgeProps> = ({ type, showLabel = true }) => {
  const config = typeMap[type] || typeMap.assumption;
  return (
    <span className={`provenance-badge ${config.class}`}>
      <span className="provenance-dot" />
      {showLabel && <span className="provenance-label">{config.label}</span>}
    </span>
  );
};

export default ProvenanceBadge;
