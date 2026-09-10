import { useState } from "react";
import useSWR from "swr";
import { createUser, getCurrentUser, login, logout, type CurrentUser } from "./api/client";
import { useSSE } from "./useSSE";
import {
  createFeatureFlag,
  getFeatureFlagByChecksum,
  getFeatureFlags,
  getSnapshotRows,
  triggerTestEvent,
  type SnapshotRow,
  type StatsigFeatureDetails,
  type StatsigFlag,
} from "./api/v1/featureFlags";

const FLAGS_SWR_KEY = "feature-flags";
const initialSnapshotFilters = {
  productid: "",
  productName: "",
  timestamp_after: "",
  timestamp_before: "",
  featureflaglastchecksum: "",
};

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
  const [showSnapshotQuery, setShowSnapshotQuery] = useState(false);
  const [snapshotFilters, setSnapshotFilters] = useState(initialSnapshotFilters);
  const [snapshotRows, setSnapshotRows] = useState<SnapshotRow[]>([]);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<StatsigFeatureDetails | null>(null);
  const [featureModalOpen, setFeatureModalOpen] = useState(false);
  const [featureDetailLoading, setFeatureDetailLoading] = useState(false);

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

  async function handleSnapshotQuery(e: React.FormEvent) {
    e.preventDefault();
    setSnapshotLoading(true);
    setSubmitError(null);

    try {
      const rows = await getSnapshotRows(snapshotFilters);
      setSnapshotRows(rows);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    } finally {
      setSnapshotLoading(false);
    }
  }

  function updateSnapshotFilter(field: keyof typeof initialSnapshotFilters, value: string) {
    setSnapshotFilters((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function openFeatureDetails(checksum: string) {
    setFeatureModalOpen(true);
    setFeatureDetailLoading(true);
    setSelectedFeature(null);
    setSubmitError(null);

    try {
      const results = await getFeatureFlagByChecksum(checksum);
      setSelectedFeature(results[0] ?? null);
      if (!results[0]) {
        setSubmitError("No feature record was found for this checksum.");
      }
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    } finally {
      setFeatureDetailLoading(false);
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

      <div className="page-actions">
        <button
          className="button button-accent button-wide"
          type="button"
          onClick={() => {
            setShowSnapshotQuery(true);
            if (snapshotRows.length === 0) {
              void getSnapshotRows(snapshotFilters).then(setSnapshotRows).catch((err) => {
                setSubmitError(err instanceof Error ? err.message : String(err));
              });
            }
          }}
        >
          Query feature flag
        </button>
      </div>

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

      {showSnapshotQuery && (
        <section className="panel query-panel">
          <div className="panel-heading">
            <span className="panel-number">04</span>
            <div><p className="panel-kicker">Query</p><h2>Snapshot record search</h2></div>
          </div>

          <form className="stacked-form query-form" onSubmit={handleSnapshotQuery}>
            <div className="query-grid">
              <label>Product ID
                <input value={snapshotFilters.productid} onChange={(e) => updateSnapshotFilter("productid", e.target.value)} placeholder="gpu_100" />
              </label>
              <label>Product name
                <input value={snapshotFilters.productName} onChange={(e) => updateSnapshotFilter("productName", e.target.value)} placeholder="gpu model 100" />
              </label>
              <label>Timestamp after
                <input type="datetime-local" value={snapshotFilters.timestamp_after} onChange={(e) => updateSnapshotFilter("timestamp_after", e.target.value)} />
              </label>
              <label>Timestamp before
                <input type="datetime-local" value={snapshotFilters.timestamp_before} onChange={(e) => updateSnapshotFilter("timestamp_before", e.target.value)} />
              </label>
              <label>Last checksum
                <input value={snapshotFilters.featureflaglastchecksum} onChange={(e) => updateSnapshotFilter("featureflaglastchecksum", e.target.value)} placeholder="sha256 checksum" />
              </label>
            </div>

            <div className="query-button-row">
              <button className="button button-accent" type="submit" disabled={snapshotLoading}>{snapshotLoading ? "Loading..." : "Apply filters"}</button>
              <button className="button button-quiet" type="button" onClick={() => setShowSnapshotQuery(false)}>Close</button>
            </div>
          </form>

          <div className="data-block query-results">
            <div className="data-heading"><span>Results</span><span>{snapshotRows.length}</span></div>
            {snapshotRows.length === 0 ? (
              <p className="empty-state">No snapshot records match the current filters.</p>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Product ID</th>
                      <th>Product name</th>
                      <th>Timestamp</th>
                      <th>Last checksum</th>
                    </tr>
                  </thead>
                  <tbody>
                    {snapshotRows.map((row) => (
                      <tr key={row.id}>
                        <td>{row.productid}</td>
                        <td>{row.productName}</td>
                        <td>{new Date(row.timestamp).toLocaleString()}</td>
                        <td>
                          <button
                            type="button"
                            className="checksum-link"
                            onClick={() => void openFeatureDetails(row.featureflaglastchecksum)}
                          >
                            {row.featureflaglastchecksum}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      )}

      {featureModalOpen && (
        <div className="feature-modal-backdrop" onClick={() => setFeatureModalOpen(false)}>
          <div className="feature-modal-card" onClick={(event) => event.stopPropagation()}>
            <div className="feature-modal-header">
              <div>
                <p className="panel-kicker">Feature details</p>
                <h3>StatsigFeatures</h3>
              </div>
              <button type="button" className="button button-quiet" onClick={() => setFeatureModalOpen(false)}>Close</button>
            </div>

            {featureDetailLoading ? (
              <p className="empty-state">Loading feature metadata...</p>
            ) : selectedFeature ? (
              <div className="feature-modal-body">
                <div className="feature-detail-grid">
                  <div>
                    <span className="field-label">Environment</span>
                    <strong>{selectedFeature.environment}</strong>
                  </div>
                  <div>
                    <span className="field-label">Checksum</span>
                    <strong className="breakable">{selectedFeature.checksum}</strong>
                  </div>
                  <div>
                    <span className="field-label">Created</span>
                    <strong>{new Date(selectedFeature.created_at).toLocaleString()}</strong>
                  </div>
                  <div>
                    <span className="field-label">Updated</span>
                    <strong>{new Date(selectedFeature.updated_at).toLocaleString()}</strong>
                  </div>
                </div>

                <div className="metadata-panel">
                  <div className="metadata-header">Metadata</div>
                  <pre>{JSON.stringify(selectedFeature.metadata ?? {}, null, 2)}</pre>
                </div>
              </div>
            ) : (
              <p className="empty-state">No matching feature record was found for this checksum.</p>
            )}
          </div>
        </div>
      )}
    </main>
  );
}