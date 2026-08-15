import { useCallback, useEffect, useState } from "react";
import { fetchComputerChecklist, toggleMaintenanceLog } from "../api/maintenanceApi";

export default function useChecklist(computerId, period, frequency) {
  const [view, setView] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savingTaskId, setSavingTaskId] = useState(null);

  const load = useCallback(async () => {
    if (!computerId || !period) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchComputerChecklist(computerId, period, frequency);
      setView(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [computerId, period, frequency]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleTask = useCallback(
    async (item, completedBy) => {
      setSavingTaskId(item.task_id);
      // Optimistic update so ticking feels instant; rolled back on failure.
      setView((prev) =>
        prev
          ? {
              ...prev,
              checklist: prev.checklist.map((row) =>
                row.task_id === item.task_id ? { ...row, completed: !row.completed } : row
              ),
            }
          : prev
      );
      try {
        await toggleMaintenanceLog({
          computerId,
          maintenanceTaskId: item.task_id,
          periodLabel: period,
          completed: !item.completed,
          completedBy,
        });
        await load();
      } catch (err) {
        setError(err);
        // Roll back the optimistic flip.
        setView((prev) =>
          prev
            ? {
                ...prev,
                checklist: prev.checklist.map((row) =>
                  row.task_id === item.task_id ? { ...row, completed: item.completed } : row
                ),
              }
            : prev
        );
      } finally {
        setSavingTaskId(null);
      }
    },
    [computerId, period, load]
  );

  return { view, error, loading, savingTaskId, toggleTask, refresh: load };
}
