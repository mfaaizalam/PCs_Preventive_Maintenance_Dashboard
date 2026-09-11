import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { CheckCircle2, Clock, AlertCircle } from "lucide-react";
import useComputerMaintenanceHistory from "../../hooks/useComputerMaintenanceHistory";
import { isPeriodElapsed, recentPeriods } from "../../utils/period";

const RING_SIZE = 88;
const RING_STROKE = 8;

function ringColor(percent) {
  if (percent >= 100) return "#1C9A6C";
  if (percent > 0) return "#C67E10";
  return "#D33B3B";
}

function CompletionRing({ percent }) {
  const radius = (RING_SIZE - RING_STROKE) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - Math.min(100, Math.max(0, percent)) / 100);
  const color = ringColor(percent);

  return (
    <div className="relative" style={{ width: RING_SIZE, height: RING_SIZE }}>
      <svg width={RING_SIZE} height={RING_SIZE} className="-rotate-90">
        <circle cx={RING_SIZE / 2} cy={RING_SIZE / 2} r={radius} fill="none" stroke="#EEF1F5" strokeWidth={RING_STROKE} />
        <circle
          cx={RING_SIZE / 2}
          cy={RING_SIZE / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={RING_STROKE}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 500ms ease, stroke 300ms ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-display text-lg font-semibold text-ink-900">{percent}%</span>
      </div>
    </div>
  );
}

export default function PCMaintenanceProgress({ checklist, frequency, period, computerId }) {
  const stats = useMemo(() => {
    const total = checklist.length;
    const completed = checklist.filter((i) => i.completed).length;
    const overdue = checklist.filter(
      (i) => !i.completed && isPeriodElapsed(frequency, period)
    ).length;
    const pending = total - completed - overdue;
    const percent = total ? Math.round((completed / total) * 100) : 0;
    return { total, completed, overdue, pending, percent };
  }, [checklist, frequency, period]);

  const trendPeriods = useMemo(() => recentPeriods(frequency, 6), [frequency]);
  const { history, loading: historyLoading } = useComputerMaintenanceHistory(
    computerId,
    frequency,
    trendPeriods
  );

  return (
    <div className="panel p-5">
      <p className="mb-4 text-sm font-semibold text-ink-800">
        This PC's maintenance tracking - {frequency.replace("_", "-")}
      </p>

      <div className="flex flex-wrap items-center gap-6">
        <CompletionRing percent={stats.percent} />

        <div className="flex flex-1 flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-signal-healthy" />
            <div>
              <p className="font-display text-lg font-semibold text-ink-900">{stats.completed}</p>
              <p className="text-[11px] text-ink-400">Done</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-signal-attention" />
            <div>
              <p className="font-display text-lg font-semibold text-ink-900">{stats.pending}</p>
              <p className="text-[11px] text-ink-400">Pending</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-signal-critical" />
            <div>
              <p className="font-display text-lg font-semibold text-ink-900">{stats.overdue}</p>
              <p className="text-[11px] text-ink-400">Overdue</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 border-t border-ink-100 pt-4">
        <p className="mb-2 text-[12px] font-medium text-ink-500">
          Last {trendPeriods.length} periods for this PC
        </p>
        {historyLoading ? (
          <p className="text-[12px] text-ink-300">Loading trend…</p>
        ) : history.length === 0 ? (
          <p className="text-[12px] text-ink-300">No history yet for this frequency.</p>
        ) : (
          <ResponsiveContainer width="100%" height={110}>
            <BarChart data={history} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" fontSize={11} tick={{ fill: "#8b95a3" }} />
              <YAxis domain={[0, 100]} fontSize={11} tick={{ fill: "#8b95a3" }} />
              <Tooltip
                formatter={(value, _name, item) => [
                  `${item.payload.completed} of ${item.payload.total} (${value}%)`,
                  "Completed",
                ]}
              />
              <Bar dataKey="percent" radius={[4, 4, 0, 0]}>
                {history.map((entry, i) => (
                  <Cell key={i} fill={ringColor(entry.percent)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}