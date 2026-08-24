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
    <main className="app-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Operations console</p>
          <h1>Feature flag control panel</h1>
          <p className="page-intro">Manage access, publish flag snapshots, and watch events arrive in real time.</p>
        </div>
        <div className="session-area">
          {user ? (
            <>
              <span className="signed-in">{user.username} <small>{user.is_staff ? "admin" : "read-only"}</small></span>
              <button className="button button-quiet" type="button" onClick={() => { logout(); setUser(null); }}>Log out</button>
            </>
          ) : (
            <form className="login-form" onSubmit={handleLogin}>
              <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" aria-label="Username" required />
              <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" aria-label="Password" type="password" required />
              <button className="button button-dark" type="submit">Sign in</button>
            </form>
          )}
        </div>
      </header>

      {submitError && <p className="error-banner" role="alert">{submitError}</p>}

      <div className="dashboard-grid">
        <section className="panel user-panel">
          <div className="panel-heading">
            <span className="panel-number">01</span>
            <div><p className="panel-kicker">Access</p><h2>Create user</h2></div>
          </div>
          {user?.is_staff ? (
            <form className="stacked-form" onSubmit={handleCreateUser}>
              <label>Username<input value={newUsername} onChange={(e) => setNewUsername(e.target.value)} placeholder="jordan.smith" required /></label>
              <label>Email <span className="optional">optional</span><input value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="jordan@example.com" type="email" /></label>
              <label>Temporary password<input value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="8 characters minimum" type="password" minLength={8} required /></label>
              <label>Role<select value={newRole} onChange={(e) => setNewRole(e.target.value as "admin" | "readonly")}><option value="readonly">Read-only</option><option value="admin">Admin</option></select></label>
              <button className="button button-accent" type="submit">Create user <span aria-hidden="true">-&gt;</span></button>
            </form>
          ) : <p className="empty-state">Sign in as an admin to create users.</p>}
        </section>

        <section className="panel flag-panel">
          <div className="panel-heading">
            <span className="panel-number">02</span>
            <div><p className="panel-kicker">Configuration</p><h2>Create feature<br />flag record</h2></div>
          </div>
          <form className="stacked-form" onSubmit={handleSubmit}>
            <label>Product<input value={product} onChange={(e) => setProduct(e.target.value)} placeholder="checkout" required /></label>
            <label>Environment<input value={environment} onChange={(e) => setEnvironment(e.target.value)} placeholder="dev" required /></label>
            <label>Last checksum<input value={checksum} onChange={(e) => setChecksum(e.target.value)} placeholder="snapshot-1" required /></label>
            <button className="button button-accent" type="submit" disabled={!user || submitting}>{submitting ? "Submitting..." : "Publish record  ->"}</button>
          </form>
          {!user && <p className="helper-text">Sign in to publish a record.</p>}
          <div className="data-block">
            <div className="data-heading"><span>Saved records</span><span>{flags?.length ?? 0}</span></div>
            {isLoading && <p className="empty-state">Loading...</p>}
            {error && <p className="error-text">Error: {String(error)}</p>}
            {flags && flags.length > 0 && <pre>{JSON.stringify(flags, null, 2)}</pre>}
            {flags && flags.length === 0 && <p className="empty-state">No feature flags yet.</p>}
          </div>
        </section>

        <section className="panel sse-panel">
          <div className="panel-heading">
            <span className="panel-number">03</span>
            <div><p className="panel-kicker">Live stream</p><h2>SSE connection<br />open</h2></div>
          </div>
          <div className={`connection-status ${state}`}><span className="status-dot" />{state}</div>
          <p className="stream-copy">Channel <strong>global</strong> is listening for backend events.</p>
          <button className="button button-outline" onClick={fireTestEvent}>Send test event <span aria-hidden="true">-&gt;</span></button>
          <div className="data-block event-block">
            <div className="data-heading"><span>Latest payload</span><span className="live-label">LIVE</span></div>
            <pre>{lastEvent ? JSON.stringify(lastEvent, null, 2) : "Waiting for an event..."}</pre>
          </div>
        </section>
      </div>
    </main>
  );
}