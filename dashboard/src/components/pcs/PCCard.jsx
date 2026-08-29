import { Link } from "react-router-dom";
import { AlertTriangle, Tag, Clock, Network, History, PlugZap, Building2, MapPin } from "lucide-react";
import StatusBadge from "../common/StatusBadge";
import MetricGauge from "../common/MetricGauge";
import EditableTag from "./EditableTag";
import { effectiveStatus, statusMeta } from "../../utils/status";
import { formatRelativeTime, formatUptime } from "../../utils/format";

const CARD_HARDWARE_ACTIVITY_LIMIT = 2;

// computer.department defaults to "IMD" and lab_section defaults to
// "CAD" server-side once a value is set; before that ever happens
// (e.g. a brand new row with neither auto-derived nor hand-edited
// yet) these are the same fallbacks shown in the UI so the card never
// renders a blank tag.
const DEFAULT_DEPARTMENT = "IMD";
const DEFAULT_LAB_NAME = "CAD";

export default function PCCard({ computer, alerts = [], onUpdateComputer }) {
  const status = effectiveStatus(computer);
  const meta = statusMeta(status);
  const hardwareActivity = (computer.recent_hardware_events || []).slice(
    0,
    CARD_HARDWARE_ACTIVITY_LIMIT
  );

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
            <EditableTag
              icon={MapPin}
              value={computer.lab_section}
              placeholder={DEFAULT_LAB_NAME}
              onSave={(v) => onUpdateComputer?.(computer.id, { lab_section: v })}
            />
            <EditableTag
              icon={Building2}
              value={computer.department}
              placeholder={DEFAULT_DEPARTMENT}
              onSave={(v) => onUpdateComputer?.(computer.id, { department: v })}
            />
            <EditableTag
              icon={Tag}
              value={computer.asset_id}
              placeholder="Asset ID"
              onSave={(v) => onUpdateComputer?.(computer.id, { asset_id: v })}
            />
          </div>
        </div>
        <StatusBadge status={status} size="sm" />
      </div>

      <div className="mt-4 flex items-center justify-around gap-2 rounded-lg bg-ink-50/70 py-3">
        <MetricGauge kind="cpu" label="CPU" value={computer.cpu_usage_percent} size={56} strokeWidth={5} />
        <MetricGauge kind="ram" label="RAM" value={computer.ram_usage_percent} size={56} strokeWidth={5} />
        <MetricGauge kind="disk" label="Disk" value={computer.disk_usage_percent} size={56} strokeWidth={5} />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-ink-400">
        <span className="inline-flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {computer.is_online ? "Online" : `Last seen ${formatRelativeTime(computer.last_seen)}`}
        </span>
        {computer.ip_address && (
          <span className="inline-flex items-center gap-1 font-mono">
            <Network className="h-3 w-3" /> {computer.ip_address}
          </span>
        )}
        {computer.uptime_seconds != null && (
          <span className="inline-flex items-center gap-1">
            up {formatUptime(computer.uptime_seconds)}
          </span>
        )}
      </div>

      {alerts.length > 0 && (
        <div className="mt-2 flex items-center gap-1 text-[12px] font-medium text-signal-attention">
          <AlertTriangle className="h-3.5 w-3.5" />
          {alerts.length} alert{alerts.length > 1 ? "s" : ""}
        </div>
      )}

      {hardwareActivity.length > 0 && (
        <div className="mt-3 border-t border-ink-100 pt-2.5">
          <p className="eyebrow flex items-center gap-1.5">
            <History className="h-3 w-3" /> Hardware activity (3d)
          </p>
          <ul className="mt-1.5 space-y-1">
            {hardwareActivity.map((event, idx) => (
              <li
                key={idx}
                className="flex items-center justify-between gap-2 text-[12px] text-ink-500"
              >
                <span className="inline-flex min-w-0 items-center gap-1 truncate">
                  <PlugZap className="h-3 w-3 shrink-0 text-ink-300" />
                  <span className="truncate">{event.message}</span>
                </span>
                <span className="shrink-0 text-ink-300">
                  {formatRelativeTime(event.occurred_at)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Link>
  );
}