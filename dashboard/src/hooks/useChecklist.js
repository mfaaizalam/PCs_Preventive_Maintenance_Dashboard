import { useCallback, useEffect, useState } from "react";
import { fetchComputerChecklist, toggleMaintenanceLog } from "../api/maintenanceApi";

const cacheKey = (computerId, period, frequency) =>
  `pm-dashboard:cache:checklist:${computerId}:${period}:${frequency}`;

function readCache(computerId, period, frequency) {
  if (!computerId || !period) return null;
  try {
    const raw = localStorage.getItem(cacheKey(computerId, period, frequency));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeCache(computerId, period, frequency, data) {
  if (!computerId || !period) return;
  try {
    localStorage.setItem(cacheKey(computerId, period, frequency), JSON.stringify(data));
  } catch {
    // ignore - storage unavailable or full
  }
}

export default function useChecklist(computerId, period, frequency) {
  const [view, setView] = useState(() => readCache(computerId, period, frequency));
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(() => readCache(computerId, period, frequency) === null);
  const [savingTaskId, setSavingTaskId] = useState(null);

  const load = useCallback(async (isBackground = false) => {
    if (!computerId || !period) return;
    if (!isBackground) setLoading(true);
    setError(null);
    try {
      const result = await fetchComputerChecklist(computerId, period, frequency);
      setView(result);
      writeCache(computerId, period, frequency, result);
    } catch (err) {
      setError(err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  }, [computerId, period, frequency]);

  // On mount, or whenever the PC/period/frequency selection changes,
  // show whatever was cached for that exact combo instantly and
  // refresh underneath - only a truly new combo with no cache shows
  // the spinner.
  useEffect(() => {
    const cached = readCache(computerId, period, frequency);
    setView(cached);
    setLoading(cached === null);
    load(cached !== null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [computerId, period, frequency]);

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
        await load(true);
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