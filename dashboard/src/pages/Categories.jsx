import { useMemo, useState } from "react";
import { FolderKanban, ChevronDown, MonitorX, PlusCircle } from "lucide-react";
import useDashboardData from "../hooks/useDashboardData";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import PCCard from "../components/pcs/PCCard";
import PCFilters from "../components/pcs/PCFilters";
import AddPCModal from "../components/pcs/AddPCModal";
import { filterComputers, sortComputers } from "../utils/pcFilters";
import { effectiveStatus } from "../utils/status";

const STATUS_SEVERITY = { critical: 0, attention: 1, offline: 2, unknown: 3, healthy: 4 };

function CategorySection({ name, computers, alertsByComputer }) {
  const [open, setOpen] = useState(true);
  const worst = computers.reduce(
    (acc, c) => Math.min(acc, STATUS_SEVERITY[effectiveStatus(c)]),
    4
  );
  const worstLabel = Object.entries(STATUS_SEVERITY).find(([, v]) => v === worst)?.[0];
  const dotClass =
    {
      critical: "bg-signal-critical",
      attention: "bg-signal-attention",
      offline: "bg-signal-offline",
      healthy: "bg-signal-healthy",
      unknown: "bg-ink-300",
    }[worstLabel] || "bg-ink-300";

  return (
    <section className="panel overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left"
      >
        <div className="flex items-center gap-3">
          <span className={`h-2.5 w-2.5 rounded-full ${dotClass}`} />
          <h2 className="font-display text-[15px] font-semibold text-ink-900">{name}</h2>
          <span className="rounded-full bg-ink-100 px-2 py-0.5 font-mono text-[12px] text-ink-500">
            {computers.length}
          </span>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-ink-400 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="border-t border-ink-100 px-5 py-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {computers.map((computer) => (
              <PCCard key={computer.id} computer={computer} alerts={alertsByComputer[computer.id] || []} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

export default function Categories() {
  const { data, error, loading, refresh } = useDashboardData();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [sort, setSort] = useState("hostname-asc");
  const [addOpen, setAddOpen] = useState(false);

  const computers = useMemo(() => data?.computers ?? [], [data]);

  const alertsByComputer = useMemo(() => {
    const map = {};
    for (const alert of data?.recent_alerts ?? []) {
      if (alert.computer_id == null) continue;
      (map[alert.computer_id] ??= []).push(alert);
    }
    return map;
  }, [data]);

  const grouped = useMemo(() => {
    const filtered = sortComputers(filterComputers(computers, { query, status, category: "all" }), sort);
    const map = new Map();
    for (const c of filtered) {
      const key = c.lab_section || "Unassigned";
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(c);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [computers, query, status, sort]);

  if (loading) return <LoadingState label="Loading categories…" />;
  if (error) return <ErrorState error={error} onRetry={refresh} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 font-display text-2xl font-semibold text-ink-900">
            <FolderKanban className="h-6 w-6 text-brand-600" />
            Categories
          </h1>
          <p className="mt-1 text-sm text-ink-400">
            PCs grouped by lab section (CAED, CAD/CAM, Office/Conference/Classroom, etc.)
          </p>
        </div>
        <button
          onClick={() => setAddOpen(true)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-700 px-3.5 py-2 text-sm font-medium text-white hover:bg-brand-800"
        >
          <PlusCircle className="h-4 w-4" />
          Add PC
        </button>
      </div>

      <AddPCModal open={addOpen} onClose={() => setAddOpen(false)} onCreated={refresh} />

      <PCFilters
        query={query}
        onQueryChange={setQuery}
        status={status}
        onStatusChange={setStatus}
        sort={sort}
        onSortChange={setSort}
      />

      {grouped.length === 0 ? (
        <EmptyState icon={MonitorX} title="No PCs match your filters" />
      ) : (
        <div className="space-y-4">
          {grouped.map(([name, list]) => (
            <CategorySection key={name} name={name} computers={list} alertsByComputer={alertsByComputer} />
          ))}
        </div>
      )}
    </div>
  );
}