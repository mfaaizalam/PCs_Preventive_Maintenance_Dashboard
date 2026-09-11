import { useEffect, useState } from "react";
import { fetchComputerChecklist } from "../api/maintenanceApi";
import { formatPeriodLabel } from "../utils/period";

export default function useComputerMaintenanceHistory(computerId, frequency, periods) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!computerId || !periods?.length) {
      setHistory([]);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    Promise.all(
      periods.map((period) =>
        fetchComputerChecklist(computerId, period, frequency, controller.signal)
          .then((view) => {
            const checklist = view.checklist || [];
            const total = checklist.length;
            const completed = checklist.filter((i) => i.completed).length;
            return {
              period,
              label: formatPeriodLabel(frequency, period),
              total,
              completed,
              percent: total ? Math.round((completed / total) * 100) : 0,
            };
          })
          .catch(() => null)
      )
    )
      .then((results) => {
        if (controller.signal.aborted) return;
        setHistory(results.filter(Boolean).reverse());
      })
      .catch((err) => !controller.signal.aborted && setError(err))
      .finally(() => !controller.signal.aborted && setLoading(false));

    return () => controller.abort();
  }, [computerId, frequency, periods]);

  return { history, loading, error };
}