import { useCallback, useMemo, useState } from "react";
import { MonitorX, Power } from "lucide-react";
import useDashboardData from "../hooks/useDashboardData";
import { updateComputer, shutdownLabSection } from "../api/computersApi";
import { acknowledgeAlert } from "../api/agentApi";
import { useAuth } from "../auth/AuthContext";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import ConfirmDialog from "../components/common/ConfirmDialog";
import StatStrip from "../components/pcs/StatStrip";
import PCFilters from "../components/pcs/PCFilters";
import PCCard from "../components/pcs/PCCard";
import AlertsPanel from "../components/pcs/AlertsPanel";
import { filterComputers, sortComputers } from "../utils/pcFilters";
import { formatDateTime } from "../utils/format";

export default function Dashboard() {
  const { data, error, loading, refresh, refreshSilent } = useDashboardData();
  const { user } = useAuth();

  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [department, setDepartment] = useState("all");
  const [labName, setLabName] = useState("all");
  const [sort, setSort] = useState("hostname-asc");

  const [shutdownDialog, setShutdownDialog] = useState(null);
  const [shuttingDown, setShuttingDown] = useState(null);

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
    const filtered = filterComputers(computers, {
      query,
      status,
      department,
      labName,
    });
    return sortComputers(filtered, sort);
  }, [computers, query, status, department, labName, sort]);

  const handleUpdateComputer = useCallback(
  async (computerId, updates) => {
    await updateComputer(computerId, updates);
    await refreshSilent();
  },
  [refreshSilent]
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

const handleDismissAlert = useCallback(
  async (alertId) => {
    await acknowledgeAlert(alertId);
    await refreshSilent();
  },
  [refreshSilent]
);

  async function confirmLabShutdown() {
    if (!shutdownDialog) return;

    const { section } = shutdownDialog;

    setShuttingDown(section);

    try {
      await shutdownLabSection(section, user?.name ?? "Dashboard");
      await refresh();
    } finally {
      setShuttingDown(null);
    }
  }

  const sections = useMemo(() => {
    const groups = new Map();

    for (const computer of visibleComputers) {
      const key = computer.lab_section || "Unassigned";

      if (!groups.has(key)) groups.set(key, []);

      groups.get(key).push(computer);
    }

    return [...groups.entries()];
  }, [visibleComputers]);

  if (loading) return <LoadingState label="Loading dashboard…" />;
  if (error) return <ErrorState error={error} onRetry={refresh} />;

  return (
    <div className="space-y-6">
      <ConfirmDialog
        open={!!shutdownDialog}
        tone="danger"
        title={`Shut down all of ${shutdownDialog?.section}?`}
        description={`This will flag ${shutdownDialog?.count} online PC${
          shutdownDialog?.count === 1 ? "" : "s"
        } in ${shutdownDialog?.section} to power off within the next check-in cycle (~10-60s per PC). Anyone logged in will see Windows' own shutdown warning first.`}
        confirmLabel="Shut down section"
        onConfirm={confirmLabShutdown}
        onClose={() => setShutdownDialog(null)}
      />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">
            Fleet Overview
          </h1>
          <p className="mt-1 text-sm text-ink-400">
            Live status for every monitored lab PC · updated{" "}
            {formatDateTime(data?.last_refresh_at)}
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
            <div className="space-y-8">
              {sections.map(([section, sectionComputers]) => {
                const onlineCount = sectionComputers.filter(
                  (c) => c.is_online
                ).length;

                return (
                  <div key={section}>
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-[12px] font-semibold uppercase tracking-wide text-ink-400">
                        {section}
                        <span className="ml-2 font-normal normal-case text-ink-300">
                          ({sectionComputers.length} PCs)
                        </span>
                      </p>

                      {onlineCount > 0 && (
                        <button
                          onClick={() =>
                            setShutdownDialog({
                              section,
                              count: onlineCount,
                            })
                          }
                          disabled={shuttingDown === section}
                          className="inline-flex items-center gap-1 rounded-md border border-signal-critical/30 bg-signal-criticalBg px-2.5 py-1 text-[12px] font-medium text-signal-critical hover:bg-signal-critical/10 disabled:opacity-60"
                          title={`Shut down all ${onlineCount} online PCs in ${section}`}
                        >
                          <Power className="h-3 w-3" />
                          {shuttingDown === section
                            ? "Shutting down…"
                            : `Shut down section (${onlineCount})`}
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                      {sectionComputers.map((computer) => (
                        <PCCard
                          key={computer.id}
                          computer={computer}
                          alerts={alertsByComputer[computer.id] || []}
                          onUpdateComputer={handleUpdateComputer}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <AlertsPanel
          alerts={data?.recent_alerts ?? []}
          computersById={computersById}
          onDismiss={handleDismissAlert}
        />
      </div>
    </div>
  );
}