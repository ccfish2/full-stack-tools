// Django API base. Point this at whichever server you're testing:
// plain HTTP daphne -> http://localhost:8000
// TLS daphne        -> https://localhost:8443

export const API_BASE =
  import.meta.env.VITE_API_BASE ||
  "http://localhost:8000/api";
const ACCESS_TOKEN_KEY = "access_token";

export function logout() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export type CurrentUser = {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  is_superuser: boolean;
};

function authHeaders(): HeadersInit {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json() as { detail?: string };
      detail = body.detail ? `: ${body.detail}` : "";
    } catch {
      // Keep the HTTP status when the response is not JSON.
    }
    throw new Error(`Login failed: ${res.status} ${res.statusText}${detail}`);
  }

  const tokens = await res.json() as { access: string; refresh: string };
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  return tokens;
}

export const getCurrentUser = () =>
  fetcher<CurrentUser>("/v1/user/");

export const createUser = (data: {
  username: string;
  email: string;
  password: string;
  role: "admin" | "readonly";
}) => post<CurrentUser>("/v1/users/", data);

export async function fetcher<T>(
  path: string,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: authHeaders(),
  });

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
      ...authHeaders(),
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