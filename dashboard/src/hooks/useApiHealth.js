import { useEffect, useState } from "react";
import client from "../api/client";

// Polls GET /health (backend/app/main.py) so the top bar can show a
// simple connected/unreachable indicator independent of any one
// page's data-loading state.
export default function useApiHealth(intervalMs = 20000) {
  const [ok, setOk] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    async function check() {
      try {
        const res = await client.get("/health", { signal: controller.signal });
        if (!cancelled) setOk(res.data?.status === "healthy");
      } catch {
        if (!cancelled) setOk(false);
      }
    }

    check();
    const id = setInterval(check, intervalMs);
    return () => {
      cancelled = true;
      controller.abort();
      clearInterval(id);
    };
  }, [intervalMs]);

  return ok;
}
