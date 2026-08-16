import NotExposedNotice from "../common/NotExposedNotice";

const SECTIONS = [
  {
    title: "RAM Slots",
    hint: "GET /api/agent/computers/{agent_id}/ram-slots",
    note: "Per-slot capacity, manufacturer, and speed (RamSlot model + RamSlotResponse schema already exist).",
  },

  {
    title: "Storage Devices",
    hint: "GET /api/agent/computers/{agent_id}/storage-devices",
    note: "Disk type, capacity, and SMART health status (StorageDevice model already exists).",
  },
  {
    title: "Installed Software",
    hint: "GET /api/agent/computers/{agent_id}/software",
    note: "Application inventory reported by the agent (InstalledSoftware model already exists).",
  },
  {
    title: "Software & License Info",
    hint: "GET /api/agent/computers/{agent_id}/licenses",
    note: "Windows/Office/VS Code activation and expiry status (SoftwareLicense model already exists).",
  },
  {
    title: "Connected Peripherals",
    hint: "GET /api/agent/computers/{agent_id}/peripherals",
    note: "Mouse, keyboard, monitor, USB storage, and other connected devices (Peripheral model already exists).",
  },
  {
    title: "Peripheral Connect / Disconnect History",
    hint: "GET /api/agent/computers/{agent_id}/peripheral-events",
    note: "Timestamped USB connect/disconnect trail (PeripheralEvent model already exists).",
  },
  {
    title: "Hardware Change History",
    hint: "GET /api/agent/computers/{agent_id}/hardware-changes",
    note: "Old → new value audit trail for hostname, IP, CPU, OS, and peripheral status changes (HardwareChangeLog model already exists).",
  },
  {
    title: "Health / Metric History",
    hint: "GET /api/agent/computers/{agent_id}/metrics-history",
    note: "CPU/RAM/disk/temperature time series for trend charts (MetricHistory model already exists).",
  },
];

export default function UnexposedSectionsGrid() {
  return (
    <div>
      <h2 className="font-display text-sm font-semibold text-ink-900">More Agent Data</h2>
      <p className="mt-1 text-sm text-ink-400">
        Collected by the agent and already modeled in the database — waiting on read endpoints.
      </p>
      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        {SECTIONS.map((s) => (
          <div key={s.title} className="panel p-5">
            <p className="text-sm font-semibold text-ink-800">{s.title}</p>
            <p className="mt-1 text-[12px] text-ink-400">{s.note}</p>
            <div className="mt-3">
              <NotExposedNotice title={s.title} endpointHint={s.hint} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
