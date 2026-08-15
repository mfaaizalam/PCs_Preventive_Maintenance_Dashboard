import { formatPeriodLabel } from "../../utils/period";

export default function PeriodSelector({ frequency, periods, value, onChange, currentPeriod }) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-[12px] font-medium text-ink-400">Period</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-ink-200 bg-white px-3 py-1.5 text-sm text-ink-700 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
      >
        {periods.map((p) => (
          <option key={p} value={p}>
            {formatPeriodLabel(frequency, p)} {p === currentPeriod ? "(current)" : ""}
          </option>
        ))}
      </select>
    </div>
  );
}
