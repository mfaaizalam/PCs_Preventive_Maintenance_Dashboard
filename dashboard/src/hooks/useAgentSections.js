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

const EMPTY = {
  ramSlots: [],
  storageDevices: [],
  installedSoftware: [],
  softwareLicenses: [],
  peripherals: [],
  peripheralEvents: [],
  hardwareChanges: [],
};

/**
 * Loads every "More Agent Data" section for one PC (RAM slots, storage
 * devices, installed software, licenses, peripherals, peripheral
 * connect/disconnect history, and hardware change history) in
 * parallel. Each of these already has a real GET route on the
 * backend - this just wires the PC details page to them instead of
 * showing the "not exposed" placeholder.
 */
export default function useAgentSections(agentId) {
  const [sections, setSections] = useState(EMPTY);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!agentId) return;
    setLoading(true);
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

  useEffect(() => {
    load();
  }, [load]);

  return { ...sections, loading, error, refresh: load };
}