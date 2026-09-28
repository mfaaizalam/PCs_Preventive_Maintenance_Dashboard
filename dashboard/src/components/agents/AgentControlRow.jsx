import { PauseCircle, PlayCircle, Network, MapPin } from "lucide-react";
import AgentStateBadge from "./AgentStateBadge";
import StatusBadge from "../common/StatusBadge";
import { effectiveStatus } from "../../utils/status";
import { formatRelativeTime } from "../../utils/format";

export default function AgentControlRow({ computer, busy, onPause, onResume }) {
  const status = effectiveStatus(computer);
  const transitioning = computer.pending_pause || computer.pending_resume;

  return (
    <tr className="border-b border-ink-100 last:border-b-0">
      <td className="px-4 py-3">
        <p className="font-display text-sm font-semibold text-ink-900">{computer.hostname}</p>
        <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[12px] text-ink-400">
          <span className="inline-flex items-center gap-1">
            <MapPin className="h-3 w-3" /> {computer.lab_section || "Unassigned"}
          </span>
          {computer.ip_address && (
            <span className="inline-flex items-center gap-1 font-mono">
              <Network className="h-3 w-3" /> {computer.ip_address}
            </span>
          )}
        </div>
      </td>

      <td className="px-4 py-3">
        <StatusBadge status={status} size="sm" />
        <p className="mt-1 text-[11px] text-ink-300">
          {computer.is_online ? "Online" : `Last seen ${formatRelativeTime(computer.last_seen)}`}
        </p>
      </td>

      <td className="px-4 py-3">
        <AgentStateBadge computer={computer} />
      </td>

      <td className="px-4 py-3 text-right">
        {computer.monitoring_paused ? (
          <button
            type="button"
            disabled={busy || transitioning}
            onClick={onResume}
            className="inline-flex items-center gap-1.5 rounded-lg bg-brand-700 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-brand-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <PlayCircle className="h-3.5 w-3.5" />
            Resume
          </button>
        ) : (
          <button
            type="button"
            disabled={busy || transitioning || !computer.is_online}
            title={!computer.is_online ? "PC must be online to flag a pause" : undefined}
            onClick={onPause}
            className="inline-flex items-center gap-1.5 rounded-lg border border-ink-200 px-3 py-1.5 text-xs font-medium text-ink-600 transition hover:bg-ink-50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <PauseCircle className="h-3.5 w-3.5" />
            Pause
          </button>
        )}
      </td>
    </tr>
  );
}