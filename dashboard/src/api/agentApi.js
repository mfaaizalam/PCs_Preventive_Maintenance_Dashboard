import client from "./client";

export function fetchDashboardOverview(signal) {
  return client.get("/api/agent/dashboard", { signal }).then((res) => res.data);
}

export function fetchHardwareNotifications(hours = 24, signal) {
  return client
    .get("/api/agent/notifications/hardware", { params: { hours }, signal })
    .then((res) => res.data);
}

export function fetchComputerByAgentId(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}`, { signal })
    .then((res) => res.data);
}

export function fetchRamSlots(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/ram-slots`, { signal })
    .then((res) => res.data);
}

export function fetchStorageDevices(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/storage-devices`, { signal })
    .then((res) => res.data);
}

export function fetchInstalledSoftware(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/installed_software`, { signal })
    .then((res) => res.data);
}

export function fetchSoftwareLicenses(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/licenses`, { signal })
    .then((res) => res.data);
}

export function fetchPeripherals(agentId, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/peripherals`, { signal })
    .then((res) => res.data);
}

export function fetchPeripheralEvents(agentId, limit = 100, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/peripheral-events`, {
      params: { limit },
      signal,
    })
    .then((res) => res.data);
}

export function fetchHardwareChanges(agentId, limit = 100, signal) {
  return client
    .get(`/api/agent/computers/${encodeURIComponent(agentId)}/hardware-changes`, {
      params: { limit },
      signal,
    })
    .then((res) => res.data);
}