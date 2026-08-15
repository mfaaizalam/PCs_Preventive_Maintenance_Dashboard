import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ClipboardList } from "lucide-react";
import useChecklist from "../hooks/useChecklist";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import FrequencyTabs from "../components/maintenance/FrequencyTabs";
import PeriodSelector from "../components/maintenance/PeriodSelector";
import ChecklistTable from "../components/maintenance/ChecklistTable";
import { useAuth } from "../auth/AuthContext";
import { periodLabelFor, recentPeriods } from "../utils/period";
import { formatGb } from "../utils/format";

export default function MaintenanceDetail() {
  const { computerId } = useParams();
  const { user } = useAuth();
  const [frequency, setFrequency] = useState("biweekly");
  const currentPeriod = useMemo(() => periodLabelFor(frequency), [frequency]);
  const periods = useMemo(() => recentPeriods(frequency, 8), [frequency]);
  const [period, setPeriod] = useState(currentPeriod);

  // Reset to the current period whenever the frequency tab changes.
  function handleFrequencyChange(next) {
    setFrequency(next);
    setPeriod(periodLabelFor(next));
  }

  const { view, error, loading, savingTaskId, toggleTask, refresh } = useChecklist(
    Number(computerId),
    period,
    frequency
  );

  // Ticking attributes the check to whoever is logged in — no name
  // prompt needed. Unticking clears completed_by along with it.
  async function handleToggle(item) {
    toggleTask(item, item.completed ? null : user?.name ?? null);
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Link
        to="/maintenance"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-400 hover:text-brand-700"
      >
        <ArrowLeft className="h-4 w-4" /> Back to maintenance
      </Link>

      {loading && !view ? (
        <LoadingState label="Loading checklist…" />
      ) : error && !view ? (
        <ErrorState error={error} onRetry={refresh} />
      ) : view ? (
        <>
          <div className="panel p-5 sm:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h1 className="flex items-center gap-2 font-display text-2xl font-semibold text-ink-900">
                  <ClipboardList className="h-6 w-6 text-brand-600" />
                  {view.hostname}
                </h1>
                <p className="mt-1 text-sm text-ink-400">
                  {[view.lab_section, view.cpu_model].filter(Boolean).join(" · ")}
                  {view.ram_total_gb && ` · ${formatGb(view.ram_total_gb)} RAM`}
                  {view.disk_total_gb && ` · ${formatGb(view.disk_total_gb)} storage`}
                </p>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-ink-100 pt-5">
              <FrequencyTabs value={frequency} onChange={handleFrequencyChange} />
              <PeriodSelector
                frequency={frequency}
                periods={periods}
                value={period}
                onChange={setPeriod}
                currentPeriod={currentPeriod}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-signal-critical/30 bg-signal-criticalBg px-4 py-2.5 text-sm text-signal-critical">
              {error.message} — the last change may not have saved. Try again.
            </div>
          )}

          {view.checklist.length === 0 ? (
            <EmptyState
              icon={ClipboardList}
              title="No tasks for this frequency"
              description="No maintenance tasks in the catalog are set to this frequency yet."
            />
          ) : (
            <ChecklistTable
              checklist={view.checklist}
              frequency={frequency}
              period={period}
              savingTaskId={savingTaskId}
              onToggle={handleToggle}
            />
          )}
        </>
      ) : null}
    </div>
  );
}