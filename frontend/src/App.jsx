import React, { useEffect, useState } from 'react';
import { trace } from '@opentelemetry/api';
import CaseSelector from './components/CaseSelector';
import TraceTimeline from './components/TraceTimeline';
import ExplanationPanel from './components/ExplanationPanel';
import { fetchCases, fetchTrace, fetchDiagnosis, diagnoseLive } from './api';
import './styles.css';

const tracer = trace.getTracer('agent-rca-ui');

export default function App() {
  const [cases, setCases] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [trace, setTrace] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [selectedStep, setSelectedStep] = useState(null);
  const [loading, setLoading] = useState(false);
  const [liveRecompute, setLiveRecompute] = useState(false);

  useEffect(() => {
    fetchCases().then(setCases).catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    const span = tracer.startSpan('ui.select_case');
    span.setAttribute('case_id', selectedId);
    setSelectedStep(null);
    setLiveRecompute(false);
    Promise.all([
      fetchTrace(selectedId),
      fetchDiagnosis(selectedId),
    ])
      .then(([t, d]) => {
        setTrace(t);
        setDiagnosis(d);
        span.end();
      })
      .catch((err) => {
        span.recordException(err);
        span.end();
        console.error(err);
      });
  }, [selectedId]);

  const handleRecomputeLive = async () => {
    if (!selectedId) return;
    const span = tracer.startSpan('ui.recompute_click');
    span.setAttribute('case_id', selectedId);
    setLoading(true);
    setLiveRecompute(true);
    try {
      const result = await diagnoseLive(selectedId);
      const newTrace = await fetchTrace(selectedId);
      setTrace(newTrace);
      setDiagnosis({
        blame_scores: result.blame_scores,
        root_causes: result.root_causes,
        explanation: result.explanation,
        original_correct: result.original_correct,
      });
      if (result.used_fallback) {
        setLiveRecompute(true);
      }
      span.setAttribute('root_causes', JSON.stringify(result.root_causes));
    } catch (err) {
      span.recordException(err);
      console.error(err);
    } finally {
      span.end();
      setLoading(false);
    }
  };

  const selectedCase = cases.find((c) => c.id === selectedId);
  const blameScores = diagnosis?.blame_scores || {};
  const rootCauses = diagnosis?.root_causes || [];

  return (
    <div className="app-container">
      <div className="particles" aria-hidden="true">
        {Array.from({ length: 15 }).map((_, i) => (
          <div key={i} className="particle" />
        ))}
      </div>

      <div className="main-content">
        <header className="header">
          <h1>Agent Root-Cause Attribution</h1>
          <p>Select a test case to view its pipeline trace and root-cause diagnosis.</p>
        </header>

        <div className="glass-card case-bar">
          <CaseSelector
            cases={cases}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>

        <div className="main-panel">
            {selectedId && trace && (
              <>
                <div className="summary-ribbon">
                  <div className="summary-status">
                    <span className={`summary-icon ${trace.is_correct ? 'pass' : 'fail'}`}>
                      {trace.is_correct ? '\u2713' : '\u2717'}
                    </span>
                    <span className={`summary-label ${trace.is_correct ? 'pass' : 'fail'}`}>
                      {trace.is_correct ? 'CORRECT' : 'INCORRECT'}
                    </span>
                  </div>
                  <div className="summary-question">{trace.question}</div>
                  {rootCauses.length > 0 && (
                    <div className="summary-root-cause">
                      Root cause{rootCauses.length > 1 ? 's' : ''}: <strong>{rootCauses.join(', ')}</strong>
                    </div>
                  )}
                </div>

                <TraceTimeline
                  trace={trace}
                  blameScores={blameScores}
                  rootCauses={rootCauses}
                  selectedStep={selectedStep}
                  onStepClick={setSelectedStep}
                />

                <div className="action-bar">
                  <button
                    className="btn-recompute"
                    onClick={handleRecomputeLive}
                    disabled={loading}
                  >
                    {loading && <span className="spinner" />}
                    {loading ? 'Recomputing...' : 'Recompute Live'}
                  </button>
                  {liveRecompute && !loading && (
                    <span className="fallback-note">using cached result</span>
                  )}
                </div>

                <div className="glass-card detail-card" style={{ padding: 20 }}>
                  <ExplanationPanel
                    step={selectedStep}
                    stepData={trace.steps?.[selectedStep]}
                    isRootCause={rootCauses.includes(selectedStep)}
                    explanation={diagnosis?.explanation?.[selectedStep]}
                    allExplanations={diagnosis?.explanation}
                  />
                </div>
              </>
            )}

            {!selectedId && (
              <div className="glass-card empty-state">
                <span className="icon">&#8678;</span>
                <p>Select a test case above to view pipeline details.</p>
              </div>
            )}
        </div>
      </div>
    </div>
  );
}
