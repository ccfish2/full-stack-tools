import { useState } from "react";
import useSWR from "swr";
import { createUser, getCurrentUser, login, logout, type CurrentUser } from "./api/client";
import { useSSE } from "./useSSE";
import {
  createFeatureFlag,
  getFeatureFlags,
  triggerTestEvent,
  type StatsigFlag,
} from "./api/v1/featureFlags";

const FLAGS_SWR_KEY = "feature-flags";

export default function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [product, setProduct] = useState("");
  const [environment, setEnvironment] = useState("dev");
  const [checksum, setChecksum] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState<"admin" | "readonly">("readonly");

  const { data: flags, isLoading, error, mutate } = useSWR<StatsigFlag[]>(
    user ? FLAGS_SWR_KEY : null,
    getFeatureFlags,
  );
  const { state, lastEvent } = useSSE("global", FLAGS_SWR_KEY);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError(null);

    try {
      await login(username, password);
      setUser(await getCurrentUser());
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);

    try {
      await createFeatureFlag({
        product,
        environment,
        last_checksum: checksum,
      });
      setProduct("");
      setChecksum("");
      await mutate();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateUser(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError(null);

    try {
      await createUser({
        username: newUsername,
        email: newEmail,
        password: newPassword,
        role: newRole,
      });
      setNewUsername("");
      setNewEmail("");
      setNewPassword("");
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    }
  }

  async function fireTestEvent() {
    try {
      await triggerTestEvent();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div style={{ fontFamily: "sans-serif", padding: 24, maxWidth: 640, margin: "0 auto" }}>
      <h1>Statsig Feature Flag Control Panel</h1>

      <form onSubmit={handleLogin} style={{ margin: "16px 0" }}>
        <h2>Admin login</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" required />
        <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" required />
        <button type="submit">Login</button>
        {user && (
          <p>
            Signed in as {user.username} {user.is_staff ? "(admin)" : "(read-only)"}
            <button type="button" onClick={() => { logout(); setUser(null); }}>Logout</button>
          </p>
        )}
      </form>

      {user?.is_staff && (
        <form onSubmit={handleCreateUser} style={{ margin: "16px 0" }}>
          <h2>Create user</h2>
          <input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} placeholder="Username" required />
          <input value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="Email" type="email" />
          <input value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Temporary password" type="password" minLength={8} required />
          <select value={newRole} onChange={(e) => setNewRole(e.target.value as "admin" | "readonly")}>
            <option value="readonly">Read-only</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit">Create user</button>
        </form>
      )}

      <form onSubmit={handleSubmit} style={{ margin: "16px 0" }}>
        <h2>Create feature flag record</h2>
        <label>
          Product
          <input value={product} onChange={(e) => setProduct(e.target.value)} placeholder="checkout" required />
        </label>
        <label>
          Environment
          <input value={environment} onChange={(e) => setEnvironment(e.target.value)} placeholder="dev" required />
        </label>
        <label>
          Last checksum
          <input value={checksum} onChange={(e) => setChecksum(e.target.value)} placeholder="snapshot-1" required />
        </label>
        <button type="submit" disabled={!user || submitting}>
          {submitting ? "Submitting..." : "Submit to Backend"}
        </button>
        {submitError && <p style={{ color: "red" }}>{submitError}</p>}
      </form>

      <hr />
      <p>SSE connection: <strong>{state}</strong></p>
      <button onClick={fireTestEvent}>POST /api/v1/trigger-events</button>
      <h2>Last SSE payload</h2>
      <pre>{lastEvent ? JSON.stringify(lastEvent, null, 2) : "(none yet)"}</pre>
      <h2>Feature Flags</h2>
      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>Error: {String(error)}</p>}
      <pre>{flags ? JSON.stringify(flags, null, 2) : "(no data)"}</pre>
    </div>
  );
}