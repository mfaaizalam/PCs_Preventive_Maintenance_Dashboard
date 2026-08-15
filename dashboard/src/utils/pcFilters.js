import { effectiveStatus } from "./status";

const STATUS_SEVERITY = { critical: 0, attention: 1, offline: 2, unknown: 3, healthy: 4 };

export function filterComputers(computers, { query, status, category }) {
  const q = query.trim().toLowerCase();

  return computers.filter((c) => {
    if (status && status !== "all" && effectiveStatus(c) !== status) return false;
    if (category && category !== "all" && (c.lab_section || "Unassigned") !== category) return false;
    if (!q) return true;
    const haystack = [c.hostname, c.asset_id, c.agent_id, c.lab_name, c.lab_section]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
}

export function sortComputers(computers, sort) {
  const list = [...computers];
  switch (sort) {
    case "hostname-desc":
      return list.sort((a, b) => b.hostname.localeCompare(a.hostname));
    case "status-severity":
      return list.sort(
        (a, b) => STATUS_SEVERITY[effectiveStatus(a)] - STATUS_SEVERITY[effectiveStatus(b)]
      );
    case "cpu-desc":
      return list.sort((a, b) => (b.cpu_usage_percent ?? -1) - (a.cpu_usage_percent ?? -1));
    case "ram-desc":
      return list.sort((a, b) => (b.ram_usage_percent ?? -1) - (a.ram_usage_percent ?? -1));
    case "last_seen-desc":
      return list.sort((a, b) => new Date(b.last_seen ?? 0) - new Date(a.last_seen ?? 0));
    case "hostname-asc":
    default:
      return list.sort((a, b) => a.hostname.localeCompare(b.hostname));
  }
}
