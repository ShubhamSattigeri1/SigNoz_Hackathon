const API_BASE = 'http://localhost:8000/api';

export async function fetchCases() {
  const res = await fetch(`${API_BASE}/cases`);
  if (!res.ok) throw new Error('Failed to fetch cases');
  return res.json();
}

export async function fetchTrace(caseId) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/trace`);
  if (!res.ok) throw new Error('Failed to fetch trace');
  return res.json();
}

export async function fetchDiagnosis(caseId) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/diagnosis`);
  if (!res.ok) throw new Error('Failed to fetch diagnosis');
  return res.json();
}

export async function diagnoseLive(caseId) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/diagnose-live`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to diagnose live');
  return res.json();
}
