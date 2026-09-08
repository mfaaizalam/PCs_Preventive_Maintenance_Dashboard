import { useCallback, useEffect, useRef, useState } from "react";
import { fetchMaintenanceComputers } from "../api/maintenanceApi";
import { useDashboardSocket } from "../context/DashboardSocketContext";

const CACHE_KEY = "pm-dashboard:cache:maintenance-computers";

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
    // ignore
  }
}

export default function useMaintenanceComputers() {
  const [computers, setComputers] = useState(() => readCache() ?? []);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(() => readCache() === null);
  const hadCacheRef = useRef(readCache() !== null);

  const load = useCallback(async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    setError(null);

    try {
      const result = await fetchMaintenanceComputers();
      setComputers(result);
      writeCache(result);
    } catch (err) {
      setError(err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  }, []);

  // Initial load - background if we already had a cached snapshot.
  useEffect(() => {
    load(hadCacheRef.current);
  }, [load]);

  // Live update - always background, never blanks the roster.
  useDashboardSocket((message) => {
    if (message?.type === "computer_updated") {
      load(true);
    }
  });

  return {
    computers,
    error,
    loading,
    refresh: load,
  };
}