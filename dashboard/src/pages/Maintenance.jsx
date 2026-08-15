import { useMemo, useState } from "react";
import { ClipboardCheck, Search, MonitorX } from "lucide-react";
import useMaintenanceComputers from "../hooks/useMaintenanceComputers";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import MaintenanceComputerCard from "../components/maintenance/MaintenanceComputerCard";

export default function Maintenance() {
  const { computers, error, loading, refresh } = useMaintenanceComputers();
  const [query, setQuery] = useState("");

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return computers;
    return computers.filter((c) =>
      [c.hostname, c.asset_id, c.lab_section, c.lab_name]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [computers, query]);

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
          Select a PC to view and tick its biweekly / monthly / half-yearly checklist.
        </p>
      </div>

      <div className="relative max-w-xs">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-300" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search PCs…"
          className="w-full rounded-lg border border-ink-200 bg-white py-2 pl-9 pr-3 text-sm text-ink-800 placeholder:text-ink-300 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
      </div>

      {visible.length === 0 ? (
        <EmptyState icon={MonitorX} title="No PCs enrolled for maintenance yet" />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {visible.map((computer) => (
            <MaintenanceComputerCard key={computer.id} computer={computer} />
          ))}
        </div>
      )}
    </div>
  );
}
