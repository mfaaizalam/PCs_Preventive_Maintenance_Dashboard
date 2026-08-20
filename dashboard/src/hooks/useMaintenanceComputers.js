import { useCallback, useEffect, useState } from "react";
import { fetchMaintenanceComputers } from "../api/maintenanceApi";
import useWebSocket from "./useWebSocket";

export default function useMaintenanceComputers() {
  const [computers, setComputers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setError(null);

    try {
      const result = await fetchMaintenanceComputers();
      setComputers(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  // Live update
  useWebSocket("/ws/dashboard", (message) => {
    if (message?.type === "computer_updated") {
      load();
    }
  });

  return {
    computers,
    error,
    loading,
    refresh: load,
  };
}