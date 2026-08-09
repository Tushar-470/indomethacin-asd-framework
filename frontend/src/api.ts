export const API_BASE = 'http://localhost:8000/api';

async function fetcher(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
  return res.json();
}

export const fetchDrugs = () => fetcher('/drugs');
export const fetchDrug = (id: string) => fetcher(`/drugs/${id}`);
export const createDrug = (data: any) => fetcher('/drugs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });

export const fetchPolymers = () => fetcher('/polymers');
export const fetchPolymer = (id: string) => fetcher(`/polymers/${id}`);
export const createPolymer = (data: any) => fetcher('/polymers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });

export const runScreening = (data: any) => fetcher('/screening/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const fetchScreeningResult = (id: string) => fetcher(`/screening/${id}`);
export const fetchHistory = () => fetcher('/history');
export const fetchVersion = () => fetcher('/version');
