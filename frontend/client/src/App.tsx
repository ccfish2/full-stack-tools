import { useState } from "react";
import useSWR from "swr";
import { useSSE } from "./useSSE";

import {
  getFeatureFlags,
  createFeatureFlag,
  triggerTestEvent,
  type StatsigFlag,
} from "./api/v1/featureFlags";

const FLAGS_SWR_KEY = "feature-flags";

export default function App() {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const {
    data: flags,
    isLoading,
    error,
    mutate,
  } = useSWR<StatsigFlag[]>(
    FLAGS_SWR_KEY,
    getFeatureFlags,
  );

  // SSE event on "global" causes the feature flags
  // to be revalidated through SWR.
  const { state, lastEvent } = useSSE(
    "global",
    FLAGS_SWR_KEY,
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    setSubmitting(true);
    setSubmitError(null);

    try {
      await createFeatureFlag({
        key,
        key2: value,
      });

      setKey("");
      setValue("");

      // Revalidate immediately instead of waiting for SSE.
      await mutate();
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : String(err),
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function fireTestEvent() {
    try {
      await triggerTestEvent();
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : String(err),
      );
    }
  }

  return (
    <div
      style={{
        fontFamily: "sans-serif",
        padding: 24,
        maxWidth: 640,
        margin: "0 auto",
      }}
    >
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
              style={{
                display: "block",
                width: "100%",
                padding: 8,
              }}
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
              style={{
                display: "block",
                width: "100%",
                padding: 8,
              }}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{ padding: "8px 16px" }}
        >
          {submitting ? "Submitting…" : "Submit to Backend"}
        </button>

        {submitError && (
          <p style={{ color: "red" }}>
            {submitError}
          </p>
        )}
      </form>

      <hr />

      <p>
        SSE connection: <strong>{state}</strong>
      </p>

      <button
        onClick={fireTestEvent}
        style={{
          padding: "8px 16px",
          marginBottom: 16,
        }}
      >
        POST /api/v1/trigger-events
      </button>

      <h2>Last SSE payload</h2>

      <pre
        style={{
          background: "#f5f5f5",
          padding: 12,
        }}
      >
        {lastEvent
          ? JSON.stringify(lastEvent, null, 2)
          : "(none yet)"}
      </pre>

      <h2>
        Feature Flags (revalidated on each SSE event)
      </h2>

      {isLoading && <p>Loading…</p>}

      {error && (
        <p style={{ color: "red" }}>
          Error: {String(error)}
        </p>
      )}

      <pre
        style={{
          background: "#f5f5f5",
          padding: 12,
        }}
      >
        {flags
          ? JSON.stringify(flags, null, 2)
          : "(no data)"}
      </pre>
    </div>
  );
}