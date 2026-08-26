import { useMemo, useState } from "react";
import { ClipboardCheck, Search, MonitorX } from "lucide-react";
import useMaintenanceComputers from "../hooks/useMaintenanceComputers";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import ComputerSeat from "../components/maintenance/ComputerSeat";

const LEGEND = [
  { key: "healthy", label: "Healthy", dot: "bg-signal-healthy" },
  { key: "attention", label: "Needs Attention", dot: "bg-signal-attention" },
  { key: "offline", label: "Offline", dot: "bg-signal-offline" },
];

const SEATS_PER_ROW = 5;

// Groups computers by lab_section, in the order they first appear
// (the backend already orders by s_no, so this preserves the same
// section grouping the original master-list Excel used).
function groupBySection(computers) {
  const groups = new Map();
  for (const computer of computers) {
    const key = computer.lab_section || "Unassigned";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(computer);
  }
  return [...groups.entries()];
}

export default function Maintenance() {
  const { computers, error, loading, refresh } = useMaintenanceComputers();
  const [query, setQuery] = useState("");

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return computers;
    return computers.filter((c) =>
      [c.hostname, c.asset_id, c.lab_section, c.lab_name, c.ip_address]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [computers, query]);

  const sections = useMemo(() => groupBySection(visible), [visible]);

  if (loading) return <LoadingState label="Loading maintenance roster…" />;
  if (error) return <ErrorState error={error} onRetry={refresh} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 font-display text-2xl font-semibold text-ink-900">
          <ClipboardCheck className="h-6 w-6 text-brand-600" />
          Preventive Maintenance
        </h1>
        <p className="mt-1 text-sm text-ink-400">
          Pick a PC below to view and tick its biweekly / monthly / half-yearly checklist.
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="relative max-w-xs flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-300" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search PCs, IP, lab…"
            className="w-full rounded-lg border border-ink-200 bg-white py-2 pl-9 pr-3 text-sm text-ink-800 placeholder:text-ink-300 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
          />
        </div>

        <div className="flex items-center gap-4">
          {LEGEND.map((item) => (
            <span key={item.key} className="inline-flex items-center gap-1.5 text-[12px] text-ink-500">
              <span className={`h-2.5 w-2.5 rounded-full ${item.dot}`} />
              {item.label}
            </span>
          ))}
        </div>
      </div>

      {visible.length === 0 ? (
        <EmptyState icon={MonitorX} title="No PCs enrolled for maintenance yet" />
      ) : (
        <div className="space-y-8">
          {sections.map(([section, sectionComputers]) => (
            <div key={section}>
              <p className="mb-3 text-[12px] font-semibold uppercase tracking-wide text-ink-400">
                {section}
                <span className="ml-2 font-normal normal-case text-ink-300">
                  ({sectionComputers.length} PCs)
                </span>
              </p>
              <div
                className="grid gap-3"
                style={{ gridTemplateColumns: `repeat(${SEATS_PER_ROW}, minmax(0, 1fr))` }}
              >
                {sectionComputers.map((computer) => (
                  <ComputerSeat key={computer.id} computer={computer} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
