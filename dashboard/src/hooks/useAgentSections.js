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

export default function useAgentSections(agentId) {
  const [sections, setSections] = useState(EMPTY);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!agentId) return;

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

      setSections({
        ramSlots,
        storageDevices,
        installedSoftware,
        softwareLicenses,
        peripherals,
        peripheralEvents,
        hardwareChanges,
      });
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  // Initial load
  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  // Live updates
  useWebSocket("/ws/dashboard", (message) => {
    if (
      message?.type === "computer_updated" &&
      message?.agent_id === agentId
    ) {
      load();
    }
  });

  return {
    ...sections,
    loading,
    error,
    refresh: load,
  };
}