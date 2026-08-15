import { metricLevel } from "../../utils/status";

const LEVEL_BAR = {
  healthy: "bg-signal-healthy",
  attention: "bg-signal-attention",
  critical: "bg-signal-critical",
  unknown: "bg-ink-200",
};

export default function MetricBar({ kind, label, value, suffix }) {
  const level = metricLevel(kind, value);
  const pct = value === null || value === undefined ? 0 : Math.min(100, Math.max(0, value));

  return (
    <div className="flex items-center gap-3">
      <span className="w-10 shrink-0 text-[11px] font-semibold uppercase tracking-wide text-ink-400">
        {label}
      </span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-ink-100">
        <div
          className={`h-full rounded-full ${LEVEL_BAR[level]}`}
          style={{ width: `${pct}%`, transition: "width 400ms ease" }}
        />
      </div>
      <span className="w-14 shrink-0 text-right font-mono text-xs text-ink-600">
        {value === null || value === undefined ? "—" : `${Math.round(value)}${suffix || "%"}`}
      </span>
    </div>
  );
}
