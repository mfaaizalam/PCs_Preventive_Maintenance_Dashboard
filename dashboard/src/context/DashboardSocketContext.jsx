import { createContext, useContext, useEffect, useRef, useCallback } from "react";

const DashboardSocketContext = createContext(null);

/**
 * Opens ONE WebSocket to /ws/dashboard for the whole app and lets any
 * number of hooks subscribe to messages via useDashboardSocket() below,
 * instead of each hook opening its own duplicate connection.
 */
export function DashboardSocketProvider({ children }) {
  const wsRef = useRef(null);
  const listenersRef = useRef(new Set());
  const attemptRef = useRef(0);
  const closedByUsRef = useRef(false);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${protocol}//${window.location.host}/ws/dashboard`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      attemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }
      for (const listener of listenersRef.current) {
        listener(data);
      }
    };

    ws.onclose = () => {
      if (closedByUsRef.current) return;
      const attempt = attemptRef.current + 1;
      attemptRef.current = attempt;
      const delay = Math.min(1000 * 2 ** attempt, 30000);
      setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    closedByUsRef.current = false;
    connect();
    return () => {
      closedByUsRef.current = true;
      wsRef.current?.close();
    };
  }, [connect]);

  const subscribe = useCallback((listener) => {
    listenersRef.current.add(listener);
    return () => listenersRef.current.delete(listener);
  }, []);

  return (
    <DashboardSocketContext.Provider value={{ subscribe }}>
      {children}
    </DashboardSocketContext.Provider>
  );
}

/** Drop-in replacement for the old useWebSocket("/ws/dashboard", onMessage) call. */
export function useDashboardSocket(onMessage) {
  const ctx = useContext(DashboardSocketContext);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!ctx) return;
    return ctx.subscribe((data) => onMessageRef.current?.(data));
  }, [ctx]);
}