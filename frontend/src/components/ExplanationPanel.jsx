import React, { useEffect, useState } from 'react';

const STEP_LABELS = { search: 'Search', tool: 'Tool', answer: 'Answer' };
const STEP_DOTS = { search: '#00d4ff', tool: '#e67e22', answer: '#8800ff' };

function TypewriterText({ text }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);
  useEffect(() => {
    setDisplayed('');
    setDone(false);
    if (!text) { setDone(true); return; }
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) { clearInterval(interval); setDone(true); }
    }, 12);
    return () => clearInterval(interval);
  }, [text]);
  return <span>{displayed}{!done && <span className="cursor" />}</span>;
}

function CodeBlock({ label, value }) {
  const str = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  return (
    <div className="split-block">
      <span className="split-label">{label}</span>
      <pre>{str}</pre>
    </div>
  );
}

export default function ExplanationPanel({ step, stepData, isRootCause, explanation, allExplanations }) {
  if (!step || !stepData) {
    return (
      <div className="detail-empty">
        <span className="empty-icon">&#9756;</span>
        <p>Click any pipeline step to inspect its input, output, and diagnosis.</p>
      </div>
    );
  }

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <span className="detail-dot" style={{ background: STEP_DOTS[step] || '#888' }} />
        <span className="detail-title">{STEP_LABELS[step]} Step</span>
        {isRootCause && <span className="detail-badge-root">ROOT CAUSE</span>}
      </div>

      <div className="split-view">
        <CodeBlock label="INPUT" value={stepData.input} />
        <div className="split-divider" />
        <CodeBlock label="OUTPUT" value={stepData.output} />
      </div>

      {isRootCause && (
        <div className="root-banner">
          <div className="root-banner-header">
            <span className="root-icon">&#9888;</span>
            <span>Root Cause Analysis</span>
          </div>
          <div className="root-banner-text">
            <TypewriterText
              text={
                allExplanations && allExplanations[step]
                  ? allExplanations[step]
                  : explanation || 'No explanation available.'
              }
            />
          </div>
        </div>
      )}

      {!isRootCause && (
        <div className="healthy-banner">
          <span className="healthy-icon">&#10003;</span>
          <span>This step executed correctly.</span>
        </div>
      )}
    </div>
  );
}
