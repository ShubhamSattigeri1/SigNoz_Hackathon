import React from 'react';

const STEP_LABELS = { search: 'Search', tool: 'Tool', answer: 'Answer' };
const STEP_ICONS = { search: '\uD83D\uDD0D', tool: '\uD83D\uDD27', answer: '\u2705' };
const STEP_COLORS = {
  search: { bar: '#00d4ff', bg: 'rgba(0,212,255,0.04)' },
  tool: { bar: '#e67e22', bg: 'rgba(230,126,34,0.04)' },
  answer: { bar: '#8800ff', bg: 'rgba(136,0,255,0.04)' },
};

function fmt(v) {
  if (typeof v === 'string') return v;
  try { return JSON.stringify(v); } catch { return String(v); }
}

function truncate(str, n = 80) {
  return str.length > n ? str.slice(0, n) + '...' : str;
}

export default function TraceTimeline({ trace, blameScores, rootCauses, selectedStep, onStepClick }) {
  const steps = ['search', 'tool', 'answer'];
  const noBlame = !blameScores || Object.keys(blameScores).length === 0;

  return (
    <div className="timeline-section">
      <div className="title-row">
        <span className="pipeline-icon">&#9881;</span>
        <h2>Pipeline Flow</h2>
      </div>

      <div className="pipeline-steps">
        {steps.map((step, idx) => {
          const score = noBlame ? 0 : (blameScores[step] || 0);
          const isRootCause = rootCauses && rootCauses.includes(step);
          const stepData = trace?.steps?.[step];
          const col = STEP_COLORS[step];
          const inText = stepData?.input ? truncate(fmt(stepData.input), 60) : '';
          const outText = stepData?.output ? truncate(fmt(stepData.output), 60) : '';

          const fillPct = Math.min(score * 100, 100);
          const meterColor = score === 0 ? '#00d4ff' : score > 0.66 ? '#ff3355' : score > 0.33 ? '#e67e22' : '#f1c40f';

          return (
            <React.Fragment key={step}>
              <div
                className={`pipeline-card${isRootCause ? ' is-root-cause' : ''}${selectedStep === step ? ' is-selected' : ''}`}
                onClick={() => onStepClick && onStepClick(step)}
                style={{
                  '--meter-color': meterColor,
                  '--meter-pct': `${fillPct}%`,
                  borderColor: isRootCause ? '#ff3355' : score > 0.66 ? '#e67e22' : 'rgba(255,255,255,0.08)',
                }}
              >
                <div className="card-header">
                  <span className="card-icon">{STEP_ICONS[step]}</span>
                  <span className="card-label">{STEP_LABELS[step]}</span>
                </div>

                <div className="card-io">
                  <div className="io-block io-in">
                    <span className="io-label">IN</span>
                    <code>{inText || '—'}</code>
                  </div>
                  <div className="io-block io-out">
                    <span className="io-label">OUT</span>
                    <code>{outText || '—'}</code>
                  </div>
                </div>

                <div className="meter-row">
                  <div className="meter-bar">
                    <div className="meter-fill" />
                  </div>
                  <span className="meter-text" style={{ color: meterColor }}>
                    {noBlame && trace?.is_correct ? 'PASS' : `${fillPct.toFixed(0)}%`}
                  </span>
                </div>

                <div className="card-status">
                  {isRootCause && <span className="status-badge-root">ROOT CAUSE</span>}
                  {noBlame && trace?.is_correct && <span className="status-badge-ok">OK</span>}
                  {step === 'answer' && !trace?.is_correct && !isRootCause && (
                    <span className="status-badge-carry">carried from prior</span>
                  )}
                </div>
              </div>

              {idx < steps.length - 1 && (
                <div className="pipeline-arrow">
                  <div className="arrow-dot" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
