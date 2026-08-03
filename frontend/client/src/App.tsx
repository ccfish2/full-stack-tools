import { useState } from "react";
import useSWR from "swr";
import { fetcher, API_BASE } from "./api";
import { useSSE } from "./useSSE";

type StatsigFlag = {
  id: number;
  key: string;
  key2: string;
  created_at: string;
};

const FLAG_ENDPOINT = "/api/statsigfeatureflag";
const TRIGGER_EVENTS_ENDPOINT = "/api/trigger-events";

export default function App() {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // SWR key -> GET /api/statsigfeatureflag, the DRF list endpoint from urls.py
  const { data: flags, isLoading, error, mutate } = useSWR<StatsigFlag[]>(
    FLAG_ENDPOINT,
    fetcher
  );

  // Subscribing to channel "global"; any SSE message triggers mutate(FLAG_ENDPOINT)
  const { state, lastEvent } = useSSE("global", FLAG_ENDPOINT);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);

    try {
      const res = await fetch(`${API_BASE}${FLAG_ENDPOINT}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, key2: value }),
      });
      if (!res.ok) throw new Error(`Save failed: ${res.status}`);

      setKey("");
      setValue("");
      mutate(); // revalidate the list immediately, don't wait for SSE
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function fireTestEvent() {
    // POST /api/trigger-events -> SSEEventViewSet.perform_create() saves the row,
    // then publish_sse_event() sends it over channel "global".
    await fetch(`${API_BASE}${TRIGGER_EVENTS_ENDPOINT}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        channel: "global",
        event_type: "message",
        payload: { message: "manual trigger", at: new Date().toISOString() },
      }),
    });
  }

  return (
    <div style={{ fontFamily: "sans-serif", padding: 24, maxWidth: 640, margin: "0 auto" }}>
      <h1>📊 Statsig Feature Flag Control Panel</h1>

      <form onSubmit={handleSubmit} style={{ margin: "16px 0" }}>
        <div style={{ marginBottom: 12 }}>
          <label>
            Key
            <input
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder='e.g., "feature_flag_1"'
              required
              style={{ display: "block", width: "100%", padding: 8 }}
            />
          </label>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>
            Value
            <input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder='e.g., "enabled"'
              required
              style={{ display: "block", width: "100%", padding: 8 }}
            />
          </label>
        </div>
        <button type="submit" disabled={submitting} style={{ padding: "8px 16px" }}>
          {submitting ? "Submitting…" : "Submit to Backend"}
        </button>
        {submitError && <p style={{ color: "red" }}>{submitError}</p>}
      </form>

      <hr />

      <p>
        SSE connection: <strong>{state}</strong>
      </p>

      <button onClick={fireTestEvent} style={{ padding: "8px 16px", marginBottom: 16 }}>
        POST /api/trigger-events
      </button>

      <h2>Last SSE payload</h2>
      <pre style={{ background: "#f5f5f5", padding: 12 }}>
        {lastEvent ? JSON.stringify(lastEvent, null, 2) : "(none yet)"}
      </pre>

      <h2>Feature Flags (revalidated on each SSE event)</h2>
      {isLoading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>Error: {String(error)}</p>}
      <pre style={{ background: "#f5f5f5", padding: 12 }}>
        {flags ? JSON.stringify(flags, null, 2) : "(no data)"}
      </pre>
    </div>
  );
}
