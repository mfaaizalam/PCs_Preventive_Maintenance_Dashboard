import { Thermometer } from "lucide-react";
import MetricGauge from "../common/MetricGauge";
import { formatGb } from "../../utils/format";

export default function SpecsPanel({ computer }) {
  return (
    <div className="panel p-5 sm:p-6">
      <h2 className="font-display text-sm font-semibold text-ink-900">Live Resource Usage</h2>
      <p className="mt-1 text-sm text-ink-400">From the most recent agent check-in.</p>

      <div className="mt-5 grid grid-cols-3 gap-4">
        <div className="flex flex-col items-center gap-3 rounded-xl2 bg-ink-50/70 py-5">
          <MetricGauge kind="cpu" label="CPU" value={computer.cpu_usage_percent} size={84} strokeWidth={8} />
          <p className="text-center text-[12px] text-ink-500">
            {computer.cpu_model || "Model unknown"}
          </p>
        </div>
        <div className="flex flex-col items-center gap-3 rounded-xl2 bg-ink-50/70 py-5">
          <MetricGauge kind="ram" label="RAM" value={computer.ram_usage_percent} size={84} strokeWidth={8} />
          <p className="text-center text-[12px] text-ink-500">{formatGb(computer.ram_total_gb)} total</p>
        </div>
        <div className="flex flex-col items-center gap-3 rounded-xl2 bg-ink-50/70 py-5">
          <MetricGauge kind="disk" label="Disk" value={computer.disk_usage_percent} size={84} strokeWidth={8} />
          <p className="text-center text-[12px] text-ink-500">{formatGb(computer.disk_total_gb)} total</p>
        </div>
      </div>

      {computer.cpu_temperature_celsius != null && (
        <div className="mt-4 flex items-center gap-2 rounded-lg border border-ink-100 bg-white px-3.5 py-2.5 text-sm text-ink-600">
          <Thermometer className="h-4 w-4 text-ink-400" />
          CPU temperature: <span className="font-mono font-medium">{computer.cpu_temperature_celsius}°C</span>
        </div>
      )}
    </div>
  );
}
