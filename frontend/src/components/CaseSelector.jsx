import React from 'react';

export default function CaseSelector({ cases, selectedId, onSelect }) {
  return (
    <div>
      <h2>Test Cases</h2>
      <div className="case-list">
        {cases.map((c) => (
          <button
            key={c.id}
            className={`case-btn${selectedId === c.id ? ' selected' : ''}`}
            onClick={() => onSelect(c.id)}
          >
            <div className="question-text">{c.question}</div>
            <span className={`status-badge ${c.is_correct ? 'pass' : 'fail'}`}>
              {c.is_correct ? 'CORRECT' : 'INCORRECT'}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
