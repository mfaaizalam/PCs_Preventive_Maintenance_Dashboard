import { useCallback, useEffect, useRef, useState } from "react";
import { fetchHardwareNotifications } from "../api/agentApi";

const LAST_SEEN_STORAGE_KEY = "pm-dashboard:hardware-notifications:last-seen-at";
const WINDOW_HOURS = 24;

/**
 * Polls GET /api/agent/notifications/hardware every 60s for the bell
 * icon: "device removed" events across all PCs in the last 24 hours.
 * The unread count is however many of those events happened after
 * the last time the user opened the notification sidebar (persisted
 * in localStorage so it survives a page reload).
 */
export default function useHardwareNotifications(pollMs = 60000) {
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState(null);
  const [lastSeenAt, setLastSeenAt] = useState(() => {
    return localStorage.getItem(LAST_SEEN_STORAGE_KEY) || null;
  });
  const controllerRef = useRef(null);

  const load = useCallback(async () => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    try {
      const result = await fetchHardwareNotifications(WINDOW_HOURS, controller.signal);
      if (controller.signal.aborted) return;
      setNotifications(result);
      setError(null);
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(err);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, pollMs);
    return () => {
      clearInterval(id);
      controllerRef.current?.abort();
    };
  }, [load, pollMs]);

  const markAllSeen = useCallback(() => {
    const now = new Date().toISOString();
    localStorage.setItem(LAST_SEEN_STORAGE_KEY, now);
    setLastSeenAt(now);
  }, []);

  const unreadCount = lastSeenAt
    ? notifications.filter((n) => new Date(n.occurred_at) > new Date(lastSeenAt)).length
    : notifications.length;

  return { notifications, unreadCount, error, markAllSeen, refresh: load };
}