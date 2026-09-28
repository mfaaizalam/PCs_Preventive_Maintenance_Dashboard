import { PauseCircle, PlayCircle } from "lucide-react";

export default function AgentControlBulkBar({
  labSection,
  pausableCount,
  resumableCount,
  busy,
  onPauseAll,
  onResumeAll,
}) {
  const scopeLabel = labSection === "all" ? "every lab" : labSection;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl2 border border-ink-100 bg-white p-4 shadow-card">
      <p className="text-sm text-ink-500">
        Bulk action applies to <span className="font-medium text-ink-800">{scopeLabel}</span>.
      </p>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy || pausableCount === 0}
          onClick={onPauseAll}
          className="inline-flex items-center gap-1.5 rounded-lg border border-ink-200 px-3.5 py-2 text-sm font-medium text-ink-600 transition hover:bg-ink-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <PauseCircle className="h-4 w-4" />
          Pause all ({pausableCount})
        </button>

        <button
          type="button"
          disabled={busy || resumableCount === 0}
          onClick={onResumeAll}
          className="inline-flex items-center gap-1.5 rounded-lg bg-brand-700 px-3.5 py-2 text-sm font-medium text-white transition hover:bg-brand-800 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <PlayCircle className="h-4 w-4" />
          Resume all ({resumableCount})
        </button>
      </div>
    </div>
  );
}