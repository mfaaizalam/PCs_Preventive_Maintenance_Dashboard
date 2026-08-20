import { useCallback, useEffect, useState } from "react";
import {
  fetchComputerByAgentId,
  fetchDashboardOverview,
} from "../api/agentApi";
import useWebSocket from "./useWebSocket";

/**
 * Loads the computer record and keeps it live through WebSocket.
 *
 * The WebSocket only tells us that something changed.
 * We then fetch the normal REST endpoints to get the latest data.
 */
export default function usePCDetail(agentId) {
  const [computer, setComputer] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [alertsLimited, setAlertsLimited] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!agentId) return;

    setError(null);

    try {
      const [computerRes, dashboardRes] = await Promise.all([
        fetchComputerByAgentId(agentId),
        fetchDashboardOverview().catch(() => null),
      ]);

      setComputer(computerRes);

      if (dashboardRes) {
        setAlerts(
          dashboardRes.recent_alerts.filter(
            (a) => a.computer_id === computerRes.id
          )
        );

        setAlertsLimited(true);
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  // Initial load
  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  // Live updates
  useWebSocket("/ws/dashboard", (message) => {
    if (
      message?.type === "computer_updated" &&
      message?.agent_id === agentId
    ) {
      load();
    }
  });

  return {
    computer,
    alerts,
    alertsLimited,
    error,
    loading,
    refresh: load,
  };
}