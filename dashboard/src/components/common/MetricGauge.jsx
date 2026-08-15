import { metricLevel } from "../../utils/status";

const LEVEL_COLOR = {
  healthy: "#1C9A6C",
  attention: "#C67E10",
  critical: "#D33B3B",
  unknown: "#B4BECC",
};

/**
 * Compact radial gauge, styled after a hardware-monitor dial cluster
 * (think BIOS/IPMI panels) rather than a generic progress bar — this
 * is the dashboard's signature visual motif, repeated at card and
 * detail-page scale.
 */
export default function MetricGauge({ kind, label, value, size = 64, strokeWidth = 6 }) {
  const level = metricLevel(kind, value);
  const color = LEVEL_COLOR[level];
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = value === null || value === undefined ? 0 : Math.min(100, Math.max(0, value));
  const offset = circumference * (1 - pct / 100);

  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#EEF1F5"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 500ms ease, stroke 300ms ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-mono text-[13px] font-medium text-ink-800">
            {value === null || value === undefined ? "—" : `${Math.round(value)}%`}
          </span>
        </div>
      </div>
      <span className="eyebrow text-ink-500">{label}</span>
    </div>
  );
}
