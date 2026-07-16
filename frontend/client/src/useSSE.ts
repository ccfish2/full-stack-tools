import { useEffect, useRef, useState } from "react";
import { useSWRConfig } from "swr";
import { API_BASE } from "./api";

type ConnectionState = "connecting" | "open" | "error" | "closed";

/**
 * Subscribes to a django-eventstream channel over SSE.
 * Every message received calls SWR's mutate() on `swrKey`, which triggers
 * a revalidation (refetch) of that key wherever it's used with useSWR().
 *
 * Backend side: core/tasks.py publish_sse_event() -> django_eventstream.send_event(channel, "message", payload)
 * Because the event type is "message" (SSE's default), EventSource.onmessage fires directly —
 * no addEventListener for a custom event name needed.
 */
export function useSSE(channel: string, swrKey: string) {
  const { mutate } = useSWRConfig();
  const [state, setState] = useState<ConnectionState>("connecting");
  const [lastEvent, setLastEvent] = useState<unknown>(null);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const url = `${API_BASE}/api/events/?channel=${encodeURIComponent(channel)}`;
    const es = new EventSource(url);
    sourceRef.current = es;

    es.onopen = () => setState("open");

    es.onmessage = (event: MessageEvent) => {
      let payload: unknown = event.data;
      try {
        payload = JSON.parse(event.data);
      } catch {
        // not JSON, keep raw string
      }
      setLastEvent(payload);
      // Re-fetch swrKey. mutate() without a data arg just triggers a revalidation.
      mutate(swrKey);
    };

    es.onerror = () => {
      // EventSource auto-reconnects on its own; this just reflects UI state.
      setState("error");
    };

    return () => {
      es.close();
      sourceRef.current = null;
    };
  }, [channel, swrKey, mutate]);

  return { state, lastEvent };
}
