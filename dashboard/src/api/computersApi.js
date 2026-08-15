import client from "./client";

/**
 * POST /api/computers
 * Manually adds a PC that has no monitoring agent installed.
 */
export function createComputer(payload) {
  return client
    .post("/api/computers", {
      hostname: payload.hostname,
      asset_id: payload.assetId || null,
      s_no: payload.sNo || null,
      lab_name: payload.labName || null,
      lab_section: payload.labSection || null,
      ip_address: payload.ipAddress || null,
      cpu_model: payload.cpuModel || null,
      os_name: payload.osName || null,
      os_version: payload.osVersion || null,
      ram_total_gb: payload.ramTotalGb || null,
      disk_total_gb: payload.diskTotalGb || null,
    })
    .then((res) => res.data);
}

/**
 * DELETE /api/computers/{id}
 */
export function deleteComputer(computerId) {
  return client.delete(`/api/computers/${computerId}`).then((res) => res.data);
}