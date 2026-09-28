import { useEffect, useRef, useCallback } from "react";
import { getWsOrigin } from "../api/client";

/**
 * Opens a WebSocket to `path` and calls `onMessage` for every JSON
 * message received. Reconnects automatically with capped exponential
 * backoff - server reboots, wifi hiccups, etc. shouldn't require
 * reloading the dashboard tab.
 *
 * CHANGED: the host used to always be `window.location.host` (i.e.
 * "wherever this page was loaded from"), which only works when the
 * frontend and backend are the same origin. It now comes from
 * getWsOrigin() (src/api/client.js), which is driven by the same
 * /server-config.json the REST client uses - so if apiBaseUrl there
 * points at the backend directly, the WebSocket follows it there too.
 */
export default function useWebSocket(path, onMessage) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const wsRef = useRef(null);
  const attemptRef = useRef(0);
  const closedByUsRef = useRef(false);

  const connect = useCallback(() => {
    const url = `${getWsOrigin()}${path}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      attemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessageRef.current?.(data);
      } catch {
        // non-JSON frame - ignore
      }
    };

    ws.onclose = () => {
      if (closedByUsRef.current) return;
      const attempt = attemptRef.current + 1;
      attemptRef.current = attempt;
      const delay = Math.min(1000 * 2 ** attempt, 30000); // cap at 30s
      setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [path]);

  useEffect(() => {
    closedByUsRef.current = false;
    connect();
    return () => {
      closedByUsRef.current = true;
      wsRef.current?.close();
    };
  }, [connect]);
}