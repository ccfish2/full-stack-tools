import useSWR from "swr";
import { fetcher, API_BASE } from "./api";
import { useSSE } from "./useSSE";

type StatsigApplication = {
  id: number;
  data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export default function App() {
  // SWR key -> GET /statsig, the DRF list endpoint already in urls.py
  const { data, isLoading, error } = useSWR<StatsigApplication[]>("/statsig", fetcher);

  // Subscribing to channel "global"; any SSE message triggers mutate("/statsig")
  const { state, lastEvent } = useSSE("global", "/statsig");

  async function fireTestEvent() {
    // POST /trigger-events -> SSEEventViewSet.perform_create() saves the row,
    // then queues publish_sse_event on Celery.
    await fetch(`${API_BASE}/trigger-events`, {
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
    <div style={{ fontFamily: "sans-serif", padding: 24, maxWidth: 640 }}>
      <h1>SSE + SWR live demo</h1>

      <p>
        SSE connection: <strong>{state}</strong>
      </p>

      <button onClick={fireTestEvent} style={{ padding: "8px 16px", marginBottom: 16 }}>
        POST /trigger-events
      </button>

      <h2>Last SSE payload</h2>
      <pre style={{ background: "#f5f5f5", padding: 12 }}>
        {lastEvent ? JSON.stringify(lastEvent, null, 2) : "(none yet)"}
      </pre>

      <h2>/statsig (SWR key, revalidated on each event)</h2>
      {isLoading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>Error: {String(error)}</p>}
      <pre style={{ background: "#f5f5f5", padding: 12 }}>
        {data ? JSON.stringify(data, null, 2) : "(no data)"}
      </pre>
    </div>
  );
}
