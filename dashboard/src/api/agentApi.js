import client from "./client";

/**
 * GET /api/agent/dashboard
 * Aggregated overview: counts by status, every computer (summary shape),
 * and the 10 most recent unresolved alerts system-wide.
 */
export function fetchDashboardOverview(signal) {
  return client.get("/api/agent/dashboard", { signal }).then((res) => res.data);
}

/**
 * GET /api/agent/computers/{agent_id}
 * Full flat record for one computer. Note: the backend only returns
 * the computer's own columns here — no nested RAM/storage/peripheral/
 * alert/history data is exposed by this endpoint today.
 */
export function fetchComputerByAgentId(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}`, { signal })
    .then((res) => res.data);
}
