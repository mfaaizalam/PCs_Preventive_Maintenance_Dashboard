import { Cpu, HardDrive, Package, KeyRound, Mouse, History } from "lucide-react";
import useAgentSections from "../../hooks/useAgentSections";
import LoadingState from "../common/LoadingState";
import ErrorState from "../common/ErrorState";
import { formatDateTime, formatDate, formatGb, titleCase } from "../../utils/format";

function SectionCard({ title, icon: Icon, count, children }) {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <p className="flex items-center gap-1.5 text-sm font-semibold text-ink-800">
          <Icon className="h-4 w-4 text-ink-400" /> {title}
        </p>
        {count != null && <span className="eyebrow">{count}</span>}
      </div>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function EmptyRow({ children }) {
  return <p className="text-[13px] text-ink-400">{children}</p>;
}

function Table({ columns, rows, rowKey }) {
  if (rows.length === 0) return <EmptyRow>No data reported by the agent yet.</EmptyRow>;
  return (
    <div className="max-h-64 overflow-y-auto">
      <table className="w-full text-left text-[12px]">
        <thead>
          <tr className="text-ink-400">
            {columns.map((col) => (
              <th key={col.key} className="pb-1.5 pr-3 font-medium">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-100">
          {rows.map((row) => (
            <tr key={rowKey(row)} className="text-ink-700">
              {columns.map((col) => (
                <td key={col.key} className="max-w-[160px] truncate py-1.5 pr-3">
                  {col.render ? col.render(row) : row[col.key] ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function UnexposedSectionsGrid({ agentId }) {
  const {
    ramSlots,
    storageDevices,
    installedSoftware,
    softwareLicenses,
    peripherals,
    peripheralEvents,
    hardwareChanges,
    loading,
    error,
    refresh,
  } = useAgentSections(agentId);

  if (loading) return <LoadingState label="Loading agent data…" compact />;
  if (error) return <ErrorState error={error} onRetry={refresh} compact />;

  return (
    <div>
      <h2 className="font-display text-sm font-semibold text-ink-900">More Agent Data</h2>
      <p className="mt-1 text-sm text-ink-400">
        Collected by the agent on every check-in and read live from the database.
      </p>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SectionCard title="RAM Slots" icon={Cpu} count={ramSlots.length}>
          <Table
            rows={ramSlots}
            rowKey={(r) => r.id}
            columns={[
              { key: "slot_number", label: "Slot" },
              { key: "capacity_gb", label: "Capacity", render: (r) => formatGb(r.capacity_gb) },
              { key: "manufacturer", label: "Manufacturer" },
              { key: "speed_mhz", label: "Speed", render: (r) => (r.speed_mhz ? `${r.speed_mhz} MHz` : "—") },
            ]}
          />
        </SectionCard>

        <SectionCard title="Storage Devices" icon={HardDrive} count={storageDevices.length}>
          <Table
            rows={storageDevices}
            rowKey={(r) => r.id}
            columns={[
              { key: "device_identifier", label: "Device" },
              { key: "device_type", label: "Type", render: (r) => titleCase(r.device_type) },
              { key: "capacity_gb", label: "Capacity", render: (r) => formatGb(r.capacity_gb) },
              { key: "health_status", label: "Health", render: (r) => titleCase(r.health_status) },
            ]}
          />
        </SectionCard>

        <SectionCard title="Installed Software" icon={Package} count={installedSoftware.length}>
          <Table
            rows={installedSoftware}
            rowKey={(r) => r.id}
            columns={[
              { key: "name", label: "Name" },
              { key: "publisher", label: "Publisher" },
              { key: "version", label: "Version" },
              { key: "install_date", label: "Installed", render: (r) => formatDate(r.install_date) },
            ]}
          />
        </SectionCard>

        <SectionCard title="Software & License Info" icon={KeyRound} count={softwareLicenses.length}>
          <Table
            rows={softwareLicenses}
            rowKey={(r) => r.id}
            columns={[
              { key: "product_name", label: "Product" },
              { key: "vendor", label: "Vendor" },
              { key: "status", label: "Status", render: (r) => titleCase(r.status) },
              { key: "expiry_date", label: "Expires", render: (r) => formatDate(r.expiry_date) },
            ]}
          />
        </SectionCard>

        <SectionCard title="Connected Peripherals" icon={Mouse} count={peripherals.length}>
          <Table
            rows={peripherals}
            rowKey={(r) => r.id}
            columns={[
              { key: "friendly_name", label: "Device", render: (r) => r.friendly_name || titleCase(r.device_type) },
              { key: "device_type", label: "Type", render: (r) => titleCase(r.device_type) },
              { key: "status", label: "Status", render: (r) => titleCase(r.status) },
              { key: "last_seen_at", label: "Last Seen", render: (r) => formatDateTime(r.last_seen_at) },
            ]}
          />
        </SectionCard>

        <SectionCard title="Peripheral Connect / Disconnect History" icon={History} count={peripheralEvents.length}>
          <Table
            rows={peripheralEvents}
            rowKey={(r) => r.id}
            columns={[
              { key: "device_type", label: "Device", render: (r) => titleCase(r.device_type) },
              { key: "event_type", label: "Event", render: (r) => titleCase(r.event_type) },
              { key: "occurred_at", label: "When", render: (r) => formatDateTime(r.occurred_at) },
            ]}
          />
        </SectionCard>

        <div className="lg:col-span-2">
          <SectionCard title="Hardware Change History" icon={History} count={hardwareChanges.length}>
            <Table
              rows={hardwareChanges}
              rowKey={(r) => r.id}
              columns={[
                { key: "field_name", label: "Field", render: (r) => titleCase(r.field_name || r.entity_type) },
                { key: "old_value", label: "Old" },
                { key: "new_value", label: "New" },
                { key: "changed_at", label: "When", render: (r) => formatDateTime(r.changed_at) },
              ]}
            />
          </SectionCard>
        </div>
      </div>
    </div>
  );
}