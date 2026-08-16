// Django API base. Point this at whichever server you're testing:
// plain HTTP daphne -> http://localhost:8000
// TLS daphne        -> https://localhost:8443

export const API_BASE =
  import.meta.env.VITE_API_BASE ||
  "http://localhost:8000/api";

export async function fetcher<T>(
  path: string,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);

  if (!res.ok) {
    throw new Error(
      `Fetch failed: ${res.status} ${res.statusText}`,
    );
  }
  return res.json();
}

export async function post<T>(
  path: string,
  body: unknown,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(
      `POST failed: ${res.status} ${res.statusText}`,
    );
  }

  return res.json();
}