import { PauseCircle, PlayCircle, Loader2 } from "lucide-react";

// Pure presentational: derives its look purely from the three
// pause/resume flags the backend already sends on every computer
// (monitoring_paused, pending_pause, pending_resume). No local state.
export default function AgentStateBadge({ computer }) {
  if (computer.pending_pause) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-signal-attentionBg px-2.5 py-1 text-xs font-medium text-signal-attention">
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        Pausing…
      </span>
    );
  }

  if (computer.pending_resume) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-signal-attentionBg px-2.5 py-1 text-xs font-medium text-signal-attention">
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        Resuming…
      </span>
    );
  }

  if (computer.monitoring_paused) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-ink-100 px-2.5 py-1 text-xs font-medium text-ink-500">
        <PauseCircle className="h-3.5 w-3.5" />
        Paused
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-signal-healthyBg px-2.5 py-1 text-xs font-medium text-signal-healthy">
      <PlayCircle className="h-3.5 w-3.5" />
      Active
    </span>
  );
}