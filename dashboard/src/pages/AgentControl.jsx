import { useCallback, useMemo, useState } from "react";
import { ShieldAlert } from "lucide-react";
import useDashboardData from "../hooks/useDashboardData";
import { useAuth } from "../auth/AuthContext";
import { pauseAgent, resumeAgent, pauseAllAgents, resumeAllAgents } from "../api/computersApi";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import ConfirmDialog from "../components/common/ConfirmDialog";
import AgentControlFilters from "../components/agents/AgentControlFilters";
import AgentControlBulkBar from "../components/agents/AgentControlBulkBar";
import AgentControlTable from "../components/agents/AgentControlTable";

export default function AgentControl() {
  const { user } = useAuth();
  const { data, error, loading, refresh, refreshSilent } = useDashboardData();

  const [query, setQuery] = useState("");
  const [labSection, setLabSection] = useState("all");
  const [busyId, setBusyId] = useState(null);
  const [bulkBusy, setBulkBusy] = useState(false);
  const [rowDialog, setRowDialog] = useState(null); // { computer, action: "pause" | "resume" }
  const [bulkDialog, setBulkDialog] = useState(null); // { action: "pause" | "resume" }

  const computers = useMemo(() => data?.computers ?? [], [data]);

  const labSectionOptions = useMemo(
    () => [...new Set(computers.map((c) => c.lab_section).filter(Boolean))].sort(),
    [computers]
  );

  const scopedComputers = useMemo(
    () => (labSection === "all" ? computers : computers.filter((c) => c.lab_section === labSection)),
    [computers, labSection]
  );

  const visibleComputers = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return scopedComputers;
    return scopedComputers.filter((c) =>
      [c.hostname, c.ip_address, c.lab_section].filter(Boolean).some((v) => v.toLowerCase().includes(q))
    );
  }, [scopedComputers, query]);

  const pausableCount = useMemo(
    () => scopedComputers.filter((c) => c.is_online && !c.monitoring_paused).length,
    [scopedComputers]
  );
  const resumableCount = useMemo(
    () => scopedComputers.filter((c) => c.monitoring_paused).length,
    [scopedComputers]
  );

  const requestedBy = user?.name || user?.username || "IT Manager";

  const handlePauseRow = useCallback((computer) => setRowDialog({ computer, action: "pause" }), []);
  const handleResumeRow = useCallback((computer) => setRowDialog({ computer, action: "resume" }), []);

  async function confirmRowDialog() {
    if (!rowDialog) return;
    const { computer, action } = rowDialog;
    setBusyId(computer.id);
    try {
      if (action === "pause") {
        await pauseAgent(computer.id, requestedBy);
      } else {
        await resumeAgent(computer.id, requestedBy);
      }
      await refreshSilent();
    } finally {
      setBusyId(null);
    }
  }

  async function confirmBulkDialog() {
    if (!bulkDialog) return;
    const scope = labSection === "all" ? null : labSection;
    setBulkBusy(true);
    try {
      if (bulkDialog.action === "pause") {
        await pauseAllAgents(requestedBy, scope);
      } else {
        await resumeAllAgents(requestedBy, scope);
      }
      await refresh();
    } finally {
      setBulkBusy(false);
    }
  }

  if (user && user.role !== "it-manager") {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="IT Manager access only"
        description="Agent Control lets an IT Manager pause or resume monitoring agents fleet-wide. Ask an IT Manager to make changes here."
      />
    );
  }

  if (loading) return <LoadingState label="Loading agents…" />;
  if (error) return <ErrorState error={error} onRetry={refresh} />;

  return (
    <div className="space-y-6">
      <ConfirmDialog
        open={!!rowDialog}
        tone="confirm"
        title={
          rowDialog?.action === "pause"
            ? `Pause monitoring on ${rowDialog?.computer.hostname}?`
            : `Resume monitoring on ${rowDialog?.computer.hostname}?`
        }
        description={
          rowDialog?.action === "pause"
            ? "The agent will stop reporting and exit on its next check-in (within ~30s). Useful for audit windows where no extra software should be running."
            : "The agent will start reporting again on its next check-in (within ~30s)."
        }
        confirmLabel={rowDialog?.action === "pause" ? "Pause agent" : "Resume agent"}
        onConfirm={confirmRowDialog}
        onClose={() => setRowDialog(null)}
      />

      <ConfirmDialog
        open={!!bulkDialog}
        tone={bulkDialog?.action === "pause" ? "danger" : "confirm"}
        title={
          bulkDialog?.action === "pause"
            ? `Pause ${pausableCount} agent${pausableCount === 1 ? "" : "s"}?`
            : `Resume ${resumableCount} agent${resumableCount === 1 ? "" : "s"}?`
        }
        description={`Scope: ${labSection === "all" ? "every lab" : labSection}. Each agent applies the flag on its own next check-in cycle, so this can take up to ~60s per PC to fully take effect.`}
        confirmLabel={bulkDialog?.action === "pause" ? "Pause all" : "Resume all"}
        onConfirm={confirmBulkDialog}
        onClose={() => setBulkDialog(null)}
      />

      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900">Agent Control</h1>
        <p className="mt-1 text-sm text-ink-400">
          Pause or resume the monitoring agent on any lab PC — one at a time, or by lab section.
        </p>
      </div>

      <AgentControlFilters
        query={query}
        onQueryChange={setQuery}
        labSection={labSection}
        onLabSectionChange={setLabSection}
        labSectionOptions={labSectionOptions}
      />

      <AgentControlBulkBar
        labSection={labSection}
        pausableCount={pausableCount}
        resumableCount={resumableCount}
        busy={bulkBusy}
        onPauseAll={() => setBulkDialog({ action: "pause" })}
        onResumeAll={() => setBulkDialog({ action: "resume" })}
      />

      {visibleComputers.length === 0 ? (
        <EmptyState title="No PCs match" description="Try clearing the search or lab filter." />
      ) : (
        <AgentControlTable
          computers={visibleComputers}
          busyId={busyId}
          onPause={handlePauseRow}
          onResume={handleResumeRow}
        />
      )}
    </div>
  );
}