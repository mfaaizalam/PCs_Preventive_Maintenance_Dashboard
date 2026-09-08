import { useCallback, useEffect, useRef, useState } from "react";
import { fetchDashboardOverview } from "../api/agentApi";
import { useDashboardSocket } from "../context/DashboardSocketContext";

const CACHE_KEY = "pm-dashboard:cache:dashboard-overview";

function readCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeCache(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data));
  } catch {
    // storage unavailable/full - not critical, just skip caching
  }
}

/**
 * Loads GET /api/agent/dashboard and keeps it live via the
 * /ws/dashboard WebSocket. On mount it shows whatever was cached
 * from the last successful load (instant, no spinner) and only
 * shows a spinner if there's truly nothing to show yet.
 */
export default function useDashboardData(pollMs = 60000) {
  const [data, setData] = useState(() => readCache());
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(() => readCache() === null);
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
      writeCache(result);
      setError(null);
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(err);
    } finally {
      if (!isBackground && !controller.signal.aborted) setLoading(false);
    }
  }, []);

  useDashboardSocket(() => {
    load(true);
  });

  useEffect(() => {
    // If we already had cached data, the very first fetch on this
    // mount is treated as a background refresh too - the cached
    // snapshot stays on screen until the real response arrives.
    load(readCache() !== null);
    const id = setInterval(() => load(true), pollMs);
    return () => {
      clearInterval(id);
      controllerRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollMs]);

  return { data, error, loading, refresh: () => load(false) };
}