import { Link } from "react-router-dom";
import { Monitor } from "lucide-react";
import { effectiveStatus } from "../../utils/status";

// Collapses the dashboard's 5-state status model down to the 3-state
// traffic light the seat map uses: healthy / needs attention / offline.
// (attention and critical both read as "needs attention" here - the
// full detail is still one click away on the PC's own page.)
const SEAT_META = {
  healthy: {
    label: "Healthy",
    seat: "border-signal-healthy bg-signal-healthyBg text-signal-healthy",
    dot: "bg-signal-healthy",
  },
  attention: {
    label: "Needs Attention",
    seat: "border-signal-attention bg-signal-attentionBg text-signal-attention",
    dot: "bg-signal-attention",
  },
  offline: {
    label: "Offline",
    seat: "border-ink-200 bg-ink-50 text-ink-400",
    dot: "bg-signal-offline",
  },
};

function seatStatus(computer) {
  const status = effectiveStatus(computer); // healthy | attention | critical | offline | unknown
  if (status === "offline" || status === "unknown") return "offline";
  if (status === "attention" || status === "critical") return "attention";
  return "healthy";
}

export default function ComputerSeat({ computer }) {
  const seat = seatStatus(computer);
  const meta = SEAT_META[seat];

  return (
    <Link
      to={`/maintenance/${computer.id}`}
      title={`${computer.hostname} · ${computer.ip_address || "no IP"} · ${meta.label}`}
      className={`group relative flex flex-col items-center rounded-t-2xl rounded-b-lg border-2 px-2 pb-2.5 pt-3 text-center shadow-card transition hover:-translate-y-0.5 hover:shadow-cardHover ${meta.seat}`}
    >
      <span className={`absolute right-1.5 top-1.5 h-2 w-2 rounded-full ${meta.dot}`} />
      <Monitor className="h-6 w-6" strokeWidth={1.75} />
      <span className="mt-1.5 w-full truncate text-[11px] font-semibold leading-tight text-ink-800">
        {computer.hostname}
      </span>
      <span className="w-full truncate font-mono text-[10px] leading-tight text-ink-400">
        {computer.ip_address || "—"}
      </span>
    </Link>
  );
}
