import client from "./client";

/**
 * GET /api/maintenance/tasks
 * The task catalog seeded from the Excel master list.
 * @param {string|null} frequency - one of the MaintenanceFrequency enum values
 */
export function fetchMaintenanceTasks(frequency, signal) {
  return client
    .get("/api/maintenance/tasks", {
      params: frequency ? { frequency } : {},
      signal,
    })
    .then((res) => res.data);
}

/**
 * GET /api/maintenance/computers
 * All PCs enrolled for maintenance tracking, master-list order.
 */
export function fetchMaintenanceComputers(signal) {
  return client.get("/api/maintenance/computers", { signal }).then((res) => res.data);
}

/**
 * GET /api/maintenance/computers/{computer_id}/checklist
 * Live specs + that PC's checklist for one period.
 * @param {number} computerId
 * @param {string} period - e.g. '2026-08-W2' (biweekly), '2026-08' (monthly), '2026-H1' (half-yearly)
 * @param {string|null} frequency
 */
export function fetchComputerChecklist(computerId, period, frequency, signal) {
  return client
    .get(`/api/maintenance/computers/${computerId}/checklist`, {
      params: { period, ...(frequency ? { frequency } : {}) },
      signal,
    })
    .then((res) => res.data);
}

/**
 * GET /api/maintenance/summary
 * Collective completion across every enrolled PC for one
 * frequency + period — powers the checklist chart.
 */
export function fetchMaintenanceSummary(frequency, period, signal) {
  return client
    .get("/api/maintenance/summary", { params: { frequency, period }, signal })
    .then((res) => res.data);
}

/**
 * POST /api/maintenance/log
 * Tick or untick one checklist item for one computer/period.
 */
export function toggleMaintenanceLog({
  computerId,
  maintenanceTaskId,
  periodLabel,
  completed,
  completedBy,
  notes,
}) {
  return client
    .post("/api/maintenance/log", {
      computer_id: computerId,
      maintenance_task_id: maintenanceTaskId,
      period_label: periodLabel,
      completed,
      completed_by: completedBy ?? null,
      notes: notes ?? null,
    })
    .then((res) => res.data);
}