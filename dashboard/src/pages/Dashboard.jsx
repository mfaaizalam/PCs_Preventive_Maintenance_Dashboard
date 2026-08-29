import { useCallback, useMemo, useState } from "react";
import { MonitorX } from "lucide-react";
import useDashboardData from "../hooks/useDashboardData";
import { updateComputer } from "../api/computersApi";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import StatStrip from "../components/pcs/StatStrip";
import PCFilters from "../components/pcs/PCFilters";
import PCCard from "../components/pcs/PCCard";
import AlertsPanel from "../components/pcs/AlertsPanel";
import { filterComputers, sortComputers } from "../utils/pcFilters";
import { formatDateTime } from "../utils/format";

export default function Dashboard() {
  const { data, error, loading, refresh } = useDashboardData();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  // Two independent filters instead of one "category" dropdown:
  // department (IMD, etc.) and lab name (lab_section - CAD, CAED,
  // etc., the same field the old single "Category" filter used).
  const [department, setDepartment] = useState("all");
  const [labName, setLabName] = useState("all");
  const [sort, setSort] = useState("hostname-asc");

  const computers = useMemo(() => data?.computers ?? [], [data]);

  const departmentOptions = useMemo(
    () => [...new Set(computers.map((c) => c.department || "IMD"))].sort(),
    [computers]
  );

  const labNameOptions = useMemo(
    () => [...new Set(computers.map((c) => c.lab_section || "Unassigned"))].sort(),
    [computers]
  );

  const visibleComputers = useMemo(() => {
    const filtered = filterComputers(computers, { query, status, department, labName });
    return sortComputers(filtered, sort);
  }, [computers, query, status, department, labName, sort]);

  // Pencil-icon edits on PCCard call this; PATCH the field, then
  // refresh the dashboard overview so the change (and any
  // department/lab-name filter it now belongs under) shows up
  // immediately instead of waiting for the next websocket push.
  const handleUpdateComputer = useCallback(
    async (computerId, updates) => {
      await updateComputer(computerId, updates);
      await refresh();
    },
    [refresh]
  );

  const alertsByComputer = useMemo(() => {
    const map = {};
    for (const alert of data?.recent_alerts ?? []) {
      if (alert.computer_id == null) continue;
      (map[alert.computer_id] ??= []).push(alert);
    }
    return map;
  }, [data]);

  const computersById = useMemo(() => {
    const map = {};
    for (const c of computers) map[c.id] = c;
    return map;
  }, [computers]);

  if (loading) return <LoadingState label="Loading dashboard…" />;
  if (error) return <ErrorState error={error} onRetry={refresh} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Fleet Overview</h1>
          <p className="mt-1 text-sm text-ink-400">
            Live status for every monitored lab PC · updated {formatDateTime(data?.last_refresh_at)}
          </p>
        </div>
      </div>

      <StatStrip overview={data} />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <PCFilters
            query={query}
            onQueryChange={setQuery}
            status={status}
            onStatusChange={setStatus}
            department={department}
            onDepartmentChange={setDepartment}
            departmentOptions={departmentOptions}
            labName={labName}
            onLabNameChange={setLabName}
            labNameOptions={labNameOptions}
            sort={sort}
            onSortChange={setSort}
          />

          {visibleComputers.length === 0 ? (
            <EmptyState
              icon={MonitorX}
              title="No PCs match your filters"
              description="Try clearing the search, status, or category filters."
            />
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {visibleComputers.map((computer) => (
                <PCCard
                  key={computer.id}
                  computer={computer}
                  alerts={alertsByComputer[computer.id] || []}
                  onUpdateComputer={handleUpdateComputer}
                />
              ))}
            </div>
          )}
        </div>

        <AlertsPanel alerts={data?.recent_alerts ?? []} computersById={computersById} />
      </div>
    </div>
  );
}