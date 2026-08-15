import { useCallback, useEffect, useState } from "react";
import { fetchMaintenanceComputers } from "../api/maintenanceApi";

export default function useMaintenanceComputers() {
  const [computers, setComputers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
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

  useEffect(() => {
    load();
  }, [load]);

  return { computers, error, loading, refresh: load };
}
