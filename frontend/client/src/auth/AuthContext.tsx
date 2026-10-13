
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

const API = "http://127.0.0.1:8000/api/v1";
const REFRESH_URL = `${API}/token/refresh/`; // Verify your actual route

type AuthUser = {
  id: number;
  username?: string;
  email?: string;
  [key: string]: unknown;
};

type AuthContextType = {
  user: AuthUser | null;
  loading: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshAccessToken = useCallback(async (): Promise<string | null> => {
    const refresh = localStorage.getItem("refreshToken");
    if (!refresh) return null;

    const response = await fetch(REFRESH_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (!response.ok) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      return null;
    }

    const data = await response.json();
    localStorage.setItem("accessToken", data.access);

    // Some configurations rotate refresh tokens.
    if (data.refresh) {
      localStorage.setItem("refreshToken", data.refresh);
    }

    return data.access;
  }, []);

  const refreshUser = useCallback(async () => {
    let access = localStorage.getItem("accessToken");

    if (!access) {
      access = await refreshAccessToken();
    }

    if (!access) {
      setUser(null);
      setLoading(false);
      return;
    }

    let response = await fetch(`${API}/users/current`, {
      headers: { Authorization: `Bearer ${access}` },
    });

    if (response.status === 401) {
      access = await refreshAccessToken();

      if (access) {
        response = await fetch(`${API}/users/current`, {
          headers: { Authorization: `Bearer ${access}` },
        });
      }
    }

    if (response.ok) {
      setUser(await response.json());
    } else if (response.status === 401 || response.status === 403) {
      setUser(null);
    } else {
      throw new Error(`Current-user request failed: ${response.status}`);
    }

    setLoading(false);
  }, [refreshAccessToken]);

  useEffect(() => {
    void refreshUser().catch((error) => {
      console.error("Unable to restore authentication:", error);
      setLoading(false);
    });
  }, [refreshUser]);

  const logout = useCallback(() => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, refreshUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}