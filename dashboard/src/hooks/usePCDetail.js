import { useCallback, useEffect, useState } from "react";
import {
  fetchComputerByAgentId,
  fetchDashboardOverview,
} from "../api/agentApi";
import { useDashboardSocket } from "../context/DashboardSocketContext";

const cacheKey = (agentId) => `pm-dashboard:cache:pc-detail:${agentId}`;

function readCache(agentId) {
  if (!agentId) return null;
  try {
    const raw = localStorage.getItem(cacheKey(agentId));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeCache(agentId, payload) {
  if (!agentId) return;
  try {
    localStorage.setItem(cacheKey(agentId), JSON.stringify(payload));
  } catch {
    // ignore - storage unavailable or full
  }
}

/**
 * Loads the computer record and keeps it live through WebSocket.
 * Shows the last cached snapshot for this agentId instantly on
 * mount / on switching PCs, then refreshes in the background.
 */
export default function usePCDetail(agentId) {
  const [computer, setComputer] = useState(() => readCache(agentId)?.computer ?? null);
  const [alerts, setAlerts] = useState(() => readCache(agentId)?.alerts ?? []);
  const [alertsLimited, setAlertsLimited] = useState(() => readCache(agentId)?.alertsLimited ?? false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(() => readCache(agentId) === null);

  const load = useCallback(async (isBackground = false) => {
    if (!agentId) return;

    if (!isBackground) setLoading(true);
    setError(null);

    try {
      const [computerRes, dashboardRes] = await Promise.all([
        fetchComputerByAgentId(agentId),
        fetchDashboardOverview().catch(() => null),
      ]);

      setComputer(computerRes);

      let nextAlerts = alerts;
      let nextAlertsLimited = alertsLimited;

      if (dashboardRes) {
        nextAlerts = dashboardRes.recent_alerts.filter(
          (a) => a.computer_id === computerRes.id
        );
        nextAlertsLimited = true;
        setAlerts(nextAlerts);
        setAlertsLimited(nextAlertsLimited);
      }

      writeCache(agentId, {
        computer: computerRes,
        alerts: nextAlerts,
        alertsLimited: nextAlertsLimited,
      });
    } catch (err) {
      setError(err);
    } finally {
      if (!isBackground) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  // Re-hydrate from cache whenever agentId changes (e.g. navigating
  // from one PC's detail page to another), then refresh underneath.
  useEffect(() => {
    const cache = readCache(agentId);
    setComputer(cache?.computer ?? null);
    setAlerts(cache?.alerts ?? []);
    setAlertsLimited(cache?.alertsLimited ?? false);
    setLoading(cache === null);
    load(cache !== null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  useDashboardSocket((message) => {
    if (
      message?.type === "computer_updated" &&
      message?.agent_id === agentId
    ) {
      load(true);
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