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

const SOCKET_REFRESH_DEBOUNCE_MS = 1500;

export default function useDashboardData(pollMs = 60000) {
  const [data, setData] = useState(() => readCache());
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(() => readCache() === null);
  const controllerRef = useRef(null);
  const debounceRef = useRef(null);

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
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => load(true), SOCKET_REFRESH_DEBOUNCE_MS);
  });

  useEffect(() => {
    load(readCache() !== null);
    const id = setInterval(() => load(true), pollMs);
    return () => {
      clearInterval(id);
      clearTimeout(debounceRef.current);
      controllerRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollMs]);

  return { data, error, loading, refresh: () => load(false) };
}