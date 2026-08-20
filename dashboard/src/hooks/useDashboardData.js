import { useCallback, useEffect, useRef, useState } from "react";
import { fetchDashboardOverview } from "../api/agentApi";
import useWebSocket from "./useWebSocket";

/**
 * Loads GET /api/agent/dashboard and keeps it live via the
 * /ws/dashboard WebSocket: whenever an agent check-in changes
 * something, the server pushes a small "computer_updated" message
 * and we refetch the full overview in the background - no reload.
 *
 * `pollMs` is now just a slow safety-net poll (default 60s) for the
 * rare case the socket is down; the socket is what makes updates
 * feel instant in the normal case.
 */
export default function useDashboardData(pollMs = 60000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const controllerRef = useRef(null);

  const load = useCallback(async (isBackground = false) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    if (!isBackground) setLoading(true);
    try {
      const result = await fetchDashboardOverview(controller.signal);
      if (controller.signal.aborted) return;
      setData(result);
      setError(null);
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(err);
    } finally {
      if (!isBackground && !controller.signal.aborted) setLoading(false);
    }
  }, []);

  useWebSocket("/ws/dashboard", (message) => {
  load(true);
});

  useEffect(() => {
    load(false);
    const id = setInterval(() => load(true), pollMs);
    return () => {
      clearInterval(id);
      controllerRef.current?.abort();
    };
  }, [load, pollMs]);

  return { data, error, loading, refresh: () => load(false) };
}