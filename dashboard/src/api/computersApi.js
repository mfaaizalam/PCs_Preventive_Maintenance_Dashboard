import client from "./client";

export function updateComputer(computerId, updates) {
  return client.patch(`/api/computers/${computerId}`, updates).then((res) => res.data);
}

export function deleteComputer(computerId) {
  return client.delete(`/api/computers/${computerId}`).then((res) => res.data);
}

export function shutdownComputer(computerId, requestedBy) {
  return client
    .post(`/api/computers/${computerId}/shutdown`, { requested_by: requestedBy })
    .then((res) => res.data);
}

export function cancelComputerShutdown(computerId) {
  return client.post(`/api/computers/${computerId}/shutdown/cancel`).then((res) => res.data);
}

export function shutdownLabSection(labSection, requestedBy) {
  return client
    .post(
      `/api/computers/shutdown-lab`,
      { requested_by: requestedBy },
      { params: { lab_section: labSection } }
    )
    .then((res) => res.data);
}

// ------------------------------------------------------------------
// AGENT MONITORING PAUSE / RESUME (audit mode) - IT Manager only.
// ------------------------------------------------------------------

export function pauseAgent(computerId, requestedBy) {
  return client
    .post(`/api/computers/${computerId}/pause-agent`, { requested_by: requestedBy })
    .then((res) => res.data);
}

export function resumeAgent(computerId, requestedBy) {
  return client
    .post(`/api/computers/${computerId}/resume-agent`, { requested_by: requestedBy })
    .then((res) => res.data);
}

export function pauseAllAgents(requestedBy, labSection) {
  return client
    .post(`/api/computers/pause-all`, { requested_by: requestedBy, lab_section: labSection || null })
    .then((res) => res.data);
}

export function resumeAllAgents(requestedBy, labSection) {
  return client
    .post(`/api/computers/resume-all`, { requested_by: requestedBy, lab_section: labSection || null })
    .then((res) => res.data);
}