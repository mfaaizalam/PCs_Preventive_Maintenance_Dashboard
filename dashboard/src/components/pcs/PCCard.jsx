import { Link } from "react-router-dom";
import { AlertTriangle, Tag, Clock } from "lucide-react";
import StatusBadge from "../common/StatusBadge";
import MetricGauge from "../common/MetricGauge";
import { effectiveStatus, statusMeta } from "../../utils/status";
import { formatRelativeTime } from "../../utils/format";

export default function PCCard({ computer, alerts = [] }) {
  const status = effectiveStatus(computer);
  const meta = statusMeta(status);

  return (
    <Link
      to={`/pcs/${encodeURIComponent(computer.agent_id)}`}
      className={`group relative flex flex-col rounded-xl2 border-l-4 border border-ink-100 bg-white p-4 shadow-card transition hover:-translate-y-0.5 hover:shadow-cardHover ${meta.border}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate font-display text-[15px] font-semibold text-ink-900">
            {computer.hostname}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[12px] text-ink-400">
            {computer.asset_id && (
              <span className="inline-flex items-center gap-1 font-mono">
                <Tag className="h-3 w-3" /> {computer.asset_id}
              </span>
            )}
            {computer.lab_section && <span>{computer.lab_section}</span>}
          </div>
        </div>
        <StatusBadge status={status} size="sm" />
      </div>

      <div className="mt-4 flex items-center justify-around gap-2 rounded-lg bg-ink-50/70 py-3">
        <MetricGauge kind="cpu" label="CPU" value={computer.cpu_usage_percent} size={56} strokeWidth={5} />
        <MetricGauge kind="ram" label="RAM" value={computer.ram_usage_percent} size={56} strokeWidth={5} />
        <MetricGauge kind="disk" label="Disk" value={computer.disk_usage_percent} size={56} strokeWidth={5} />
      </div>

      <div className="mt-3 flex items-center justify-between text-[12px] text-ink-400">
        <span className="inline-flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {computer.is_online ? "Online" : `Last seen ${formatRelativeTime(computer.last_seen)}`}
        </span>
        {alerts.length > 0 && (
          <span className="inline-flex items-center gap-1 font-medium text-signal-attention">
            <AlertTriangle className="h-3.5 w-3.5" />
            {alerts.length} alert{alerts.length > 1 ? "s" : ""}
          </span>
        )}
      </div>
    </Link>
  );
}
