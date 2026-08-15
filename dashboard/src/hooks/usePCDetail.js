import { useCallback, useEffect, useState } from "react";
import { fetchComputerByAgentId, fetchDashboardOverview } from "../api/agentApi";

/**
 * Loads GET /api/agent/computers/{agent_id} for the flat computer
 * record, plus GET /api/agent/dashboard so this PC's alerts can be
 * filtered out of the shared recent-alerts feed (there's no per-PC
 * alerts endpoint yet — see NotExposedNotice for the sections that
 * genuinely have no data source at all).
 */
export default function usePCDetail(agentId) {
  const [computer, setComputer] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [alertsLimited, setAlertsLimited] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [computerRes, dashboardRes] = await Promise.all([
        fetchComputerByAgentId(agentId),
        fetchDashboardOverview().catch(() => null),
      ]);
      setComputer(computerRes);
      if (dashboardRes) {
        setAlerts(dashboardRes.recent_alerts.filter((a) => a.computer_id === computerRes.id));
        setAlertsLimited(true); // the feed is capped to 10 system-wide, so this is a partial view
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    load();
  }, [load]);

  return { computer, alerts, alertsLimited, error, loading, refresh: load };
}
