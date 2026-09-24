import { useCallback, useEffect, useState } from "react";
import {
  fetchRamSlots,
  fetchStorageDevices,
  fetchInstalledSoftware,
  fetchSoftwareLicenses,
  fetchPeripherals,
  fetchPeripheralEvents,
  fetchHardwareChanges,
} from "../api/agentApi";
import useWebSocket from "./useWebSocket";

const EMPTY = {
  ramSlots: [],
  storageDevices: [],
  installedSoftware: [],
  softwareLicenses: [],
  peripherals: [],
  peripheralEvents: [],
  hardwareChanges: [],
};

const cacheKey = (agentId) => `pm-dashboard:cache:agent-sections:${agentId}`;

function readCache(agentId) {
  if (!agentId) return null;
  try {
    const raw = localStorage.getItem(cacheKey(agentId));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeCache(agentId, data) {
  if (!agentId) return;
  try {
    localStorage.setItem(cacheKey(agentId), JSON.stringify(data));
  } catch {
    // ignore
  }
}

export default function useAgentSections(agentId) {
  const [sections, setSections] = useState(() => readCache(agentId) ?? EMPTY);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(() => readCache(agentId) === null);

  const load = useCallback(async (isBackground = false) => {
    if (!agentId) return;

    if (!isBackground) setLoading(true);
    setError(null);

    try {
      const [
        ramSlots,
        storageDevices,
        installedSoftware,
        softwareLicenses,
        peripherals,
        peripheralEvents,
        hardwareChanges,
      ] = await Promise.all([
        fetchRamSlots(agentId),
        fetchStorageDevices(agentId),
        fetchInstalledSoftware(agentId),
        fetchSoftwareLicenses(agentId),
        fetchPeripherals(agentId),
        fetchPeripheralEvents(agentId, 50),
        fetchHardwareChanges(agentId, 50),
      ]);

      const next = {
        ramSlots,
        storageDevices,
        installedSoftware,
        softwareLicenses,
        peripherals,
        peripheralEvents,
        hardwareChanges,
      };

      setSections(next);
      writeCache(agentId, next);
    } catch (err) {
      // Cached snapshot exists -> keep showing it, don't replace the section with an error.
      if (readCache(agentId) === null) setError(err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  }, [agentId]);

  // Re-hydrate from cache whenever agentId changes (navigating
  // between PCs), then refresh underneath.
  useEffect(() => {
    const cached = readCache(agentId);
    setSections(cached ?? EMPTY);
    setLoading(cached === null);
    load(cached !== null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  // Live updates - always background.
  useWebSocket("/ws/dashboard", (message) => {
    if (
      message?.type === "computer_updated" &&
      message?.agent_id === agentId
    ) {
      load(true);
    }
  });

  return {
    ...sections,
    loading,
    error,
    refresh: load,
  };
}