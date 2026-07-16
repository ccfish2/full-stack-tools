// Django API base. Point this at whichever server you're testing:
// plain HTTP daphne -> http://localhost:8000
// TLS daphne        -> https://localhost:8443
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const fetcher = (path: string) =>
  fetch(`${API_BASE}${path}`).then((res) => {
    if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
    return res.json();
  });
