import { useCallback, useEffect, useRef, useState } from "react";
import { fetchDashboardOverview } from "../api/agentApi";

/**
 * Loads GET /api/agent/dashboard and refreshes it on an interval so
 * PC cards, alerts, and category views reflect the latest agent
 * check-ins without a manual reload.
 */
export default function useDashboardData(pollMs = 15000) {
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
      if (controller.signal.aborted) return; // superseded by a newer call
      setData(result);
      setError(null);
    } catch (err) {
      if (controller.signal.aborted) return; // this call was canceled, not a real failure
      setError(err);
    } finally {
      if (!isBackground && !controller.signal.aborted) setLoading(false);
    }
  }, []);

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
