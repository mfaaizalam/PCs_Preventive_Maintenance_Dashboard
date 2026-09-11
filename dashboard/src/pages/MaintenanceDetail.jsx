import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ClipboardList } from "lucide-react";
import useChecklist from "../hooks/useChecklist";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import ConfirmDialog from "../components/common/ConfirmDialog";
import FrequencyTabs from "../components/maintenance/FrequencyTabs";
import PeriodSelector from "../components/maintenance/PeriodSelector";
import ChecklistTable from "../components/maintenance/ChecklistTable";
import PCMaintenanceProgress from "../components/maintenance/PCMaintenanceProgress";
import PrintExportButton from "../components/maintenance/PrintExportButton";
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
  const [dialog, setDialog] = useState(null);

  function handleFrequencyChange(next) {
    setFrequency(next);
    setPeriod(periodLabelFor(next));
  }

  const { view, error, loading, savingTaskId, toggleTask, refresh } = useChecklist(
    Number(computerId),
    period,
    frequency
  );

  function handleToggle(item) {
    const responsible = item.responsible_person?.trim();
    const isMine = !responsible || responsible.toLowerCase() === user?.name?.toLowerCase();

    if (!isMine) {
      setDialog({
        tone: "blocked",
        title: "Not your task",
        description: `"${item.task_name}" is assigned to ${responsible}. Only they (or an IT Manager) can check it off - ask them to tick it, or log in as them if that's you.`,
      });
      return;
    }

    setDialog({
      tone: "confirm",
      title: item.completed ? "Mark as not done?" : "Mark as done?",
      description: item.completed
        ? `This will un-tick "${item.task_name}" for this period.`
        : `This will tick "${item.task_name}" as completed by ${user?.name ?? "you"} for this period.`,
      confirmLabel: item.completed ? "Mark not done" : "Mark done",
      onConfirm: () => toggleTask(item, item.completed ? null : user?.name ?? null),
    });
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <ConfirmDialog
        open={!!dialog}
        title={dialog?.title}
        description={dialog?.description}
        confirmLabel={dialog?.confirmLabel}
        tone={dialog?.tone}
        onConfirm={dialog?.onConfirm}
        onClose={() => setDialog(null)}
      />

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
              <div className="flex flex-wrap items-center gap-3">
                <PeriodSelector
                  frequency={frequency}
                  periods={periods}
                  value={period}
                  onChange={setPeriod}
                  currentPeriod={currentPeriod}
                />
                <PrintExportButton
                  frequency={frequency}
                  period={period}
                  computerId={view.computer_id}
                  hostname={view.hostname}
                />
              </div>
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
            <>
              <PCMaintenanceProgress
                checklist={view.checklist}
                frequency={frequency}
                period={period}
                computerId={view.computer_id}
              />
              <ChecklistTable
                checklist={view.checklist}
                frequency={frequency}
                period={period}
                savingTaskId={savingTaskId}
                onToggle={handleToggle}
              />
            </>
          )}
        </>
      ) : null}
    </div>
  );
}