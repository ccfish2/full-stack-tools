import { useEffect, useRef, useState } from "react";
import { useSWRConfig } from "swr";
import { API_BASE } from "./api/client";

/**
 * Subscribe to a django-eventstream channel over SSE.
 *
 * Every SSE message causes the supplied SWR key to revalidate.
 *
 * Backend:
 *   django_eventstream.send_event(
 *       channel,
 *       "message",
 *       payload,
 *   )
 *
 * SSE endpoint:
 *   /api/events/?channel=<channel>
 */
type ConnectionState =
  | "connecting"
  | "open"
  | "error"
  | "closed";

export function useSSE(
  channel: string,
  swrKey: string,
) {
  const { mutate } = useSWRConfig();

  const [state, setState] =
    useState<ConnectionState>("connecting");

  const [lastEvent, setLastEvent] =
    useState<unknown>(null);

  const sourceRef =
    useRef<EventSource | null>(null);

  useEffect(() => {
    const url =
      `${API_BASE}/events/?channel=${encodeURIComponent(channel)}`;

    const es = new EventSource(url);

    sourceRef.current = es;

    es.onopen = () => {
      setState("open");
    };

    es.onmessage = (event: MessageEvent) => {
      let payload: unknown = event.data;

      try {
        payload = JSON.parse(event.data);
      } catch {
        // Keep raw string if event isn't JSON.
      }

      setLastEvent(payload);

      mutate(swrKey);
    };

    es.onerror = () => {
      setState("error");
    };

    return () => {
      es.close();
      sourceRef.current = null;
      setState("closed");
    };
  }, [channel, swrKey, mutate]);

  return {
    state,
    lastEvent,
  };
}