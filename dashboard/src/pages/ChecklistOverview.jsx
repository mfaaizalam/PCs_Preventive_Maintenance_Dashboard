import { useEffect, useMemo, useState } from "react";
import { BarChart3 } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend,
} from "recharts";
import { fetchMaintenanceSummary } from "../api/maintenanceApi";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import FrequencyTabs from "../components/maintenance/FrequencyTabs";
import PeriodSelector from "../components/maintenance/PeriodSelector";
import PrintExportButton from "../components/maintenance/PrintExportButton";
import { periodLabelFor, recentPeriods } from "../utils/period";

const COLORS = ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#0891b2", "#be185d"];
const PIE_COLORS = { done: "#16a34a", remaining: "#e5e7eb" };

export default function ChecklistOverview() {
  const [frequency, setFrequency] = useState("biweekly");
  const currentPeriod = useMemo(() => periodLabelFor(frequency), [frequency]);
  const periods = useMemo(() => recentPeriods(frequency, 8), [frequency]);
  const [period, setPeriod] = useState(currentPeriod);

  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  function handleFrequencyChange(next) {
    setFrequency(next);
    setPeriod(periodLabelFor(next));
  }

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    fetchMaintenanceSummary(frequency, period, controller.signal)
      .then((data) => !controller.signal.aborted && setSummary(data))
      .catch((err) => !controller.signal.aborted && setError(err))
      .finally(() => !controller.signal.aborted && setLoading(false));
    return () => controller.abort();
  }, [frequency, period]);

  const pieData = summary
    ? [
        { name: "Completed", value: summary.completed_count, key: "done" },
        { name: "Remaining", value: Math.max(summary.total_count - summary.completed_count, 0), key: "remaining" },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 font-display text-2xl font-semibold text-ink-900">
          <BarChart3 className="h-6 w-6 text-brand-600" />
          Checklist Overview
        </h1>
        <p className="mt-1 text-sm text-ink-400">
          The whole preventive-maintenance checklist, rolled up across every enrolled PC.
        </p>
      </div>

      <div className="panel flex flex-wrap items-center justify-between gap-3 p-4">
        <FrequencyTabs value={frequency} onChange={handleFrequencyChange} />
        <div className="flex flex-wrap items-center gap-3">
          <PeriodSelector
            frequency={frequency}
            periods={periods}
            value={period}
            onChange={setPeriod}
            currentPeriod={currentPeriod}
          />
          <PrintExportButton frequency={frequency} period={period} />
        </div>
      </div>

      {loading && !summary ? (
        <LoadingState label="Loading checklist overview…" />
      ) : error ? (
        <ErrorState error={error} onRetry={() => setPeriod((p) => p)} />
      ) : !summary || summary.total_tasks === 0 ? (
        <EmptyState
          icon={BarChart3}
          title="No tasks for this frequency"
          description="No maintenance tasks in the catalog are set to this frequency yet."
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="panel p-5">
              <p className="text-[12px] font-medium text-ink-400">Overall completion</p>
              <p className="mt-1 font-display text-3xl font-semibold text-ink-900">
                {summary.percent}%
              </p>
              <p className="mt-1 text-[12px] text-ink-400">
                {summary.completed_count} of {summary.total_count} checks done
              </p>
            </div>
            <div className="panel p-5">
              <p className="text-[12px] font-medium text-ink-400">PCs enrolled</p>
              <p className="mt-1 font-display text-3xl font-semibold text-ink-900">
                {summary.total_computers}
              </p>
            </div>
            <div className="panel p-5">
              <p className="text-[12px] font-medium text-ink-400">Tasks this frequency</p>
              <p className="mt-1 font-display text-3xl font-semibold text-ink-900">
                {summary.total_tasks}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="panel p-5 lg:col-span-2">
              <p className="mb-3 text-sm font-semibold text-ink-800">Completion by task</p>
              <ResponsiveContainer width="100%" height={Math.max(summary.by_task.length * 42, 200)}>
                <BarChart data={summary.by_task} layout="vertical" margin={{ left: 12, right: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} unit="%" fontSize={12} />
                  <YAxis
                    type="category"
                    dataKey="task_name"
                    width={220}
                    fontSize={12}
                    tick={{ fill: "#57534e" }}
                  />
                  <Tooltip
                    formatter={(value, _name, item) => [
                      `${item.payload.completed_count} of ${item.payload.total_count} PCs (${value}%)`,
                      "Completed",
                    ]}
                  />
                  <Bar dataKey="percent" radius={[0, 4, 4, 0]}>
                    {summary.by_task.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="panel p-5">
              <p className="mb-3 text-sm font-semibold text-ink-800">Overall done vs. remaining</p>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85}>
                    {pieData.map((entry) => (
                      <Cell key={entry.key} fill={PIE_COLORS[entry.key]} />
                    ))}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel p-5">
            <p className="mb-3 text-sm font-semibold text-ink-800">Completion by lab section</p>
            <ResponsiveContainer width="100%" height={Math.max(summary.by_lab_section.length * 42, 200)}>
              <BarChart data={summary.by_lab_section} layout="vertical" margin={{ left: 12, right: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} unit="%" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="lab_section"
                  width={200}
                  fontSize={12}
                  tick={{ fill: "#57534e" }}
                />
                <Tooltip
                  formatter={(value, _name, item) => [
                    `${item.payload.completed_count} of ${item.payload.total_count} checks (${value}%)`,
                    "Completed",
                  ]}
                />
                <Bar dataKey="percent" radius={[0, 4, 4, 0]} fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}