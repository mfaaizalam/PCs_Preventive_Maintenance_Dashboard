import { ArrowLeft, Tag, Network, MapPin, Cpu } from "lucide-react";
import { Link } from "react-router-dom";
import StatusBadge from "../common/StatusBadge";
import { effectiveStatus } from "../../utils/status";
import { formatDateTime, formatUptime } from "../../utils/format";

export default function PCDetailHeader({ computer }) {
  const status = effectiveStatus(computer);

  const facts = [
    { icon: Tag, label: "Asset ID", value: computer.asset_id || "—" },
    { icon: Network, label: "IP Address", value: computer.ip_address || "—" },
    { icon: MapPin, label: "Location", value: [computer.lab_name, computer.lab_section].filter(Boolean).join(" · ") || "—" },
    { icon: Cpu, label: "OS", value: [computer.os_name, computer.os_version].filter(Boolean).join(" ") || "—" },
  ];

  return (
    <div className="panel p-5 sm:p-6">
      <Link
        to="/"
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-ink-400 hover:text-brand-700"
      >
        <ArrowLeft className="h-4 w-4" /> Back to dashboard
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-display text-2xl font-semibold text-ink-900">{computer.hostname}</h1>
            <StatusBadge status={status} />
          </div>
          <p className="mt-1.5 text-sm text-ink-400">
            Agent ID <span className="font-mono text-ink-500">{computer.agent_id}</span> ·{" "}
            {computer.is_online ? "Online" : "Offline"} · last check-in{" "}
            {formatDateTime(computer.last_seen)}
            {computer.uptime_seconds != null && ` · up ${formatUptime(computer.uptime_seconds)}`}
          </p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4 border-t border-ink-100 pt-5 sm:grid-cols-4">
        {facts.map(({ icon: Icon, label, value }) => (
          <div key={label}>
            <p className="eyebrow flex items-center gap-1.5">
              <Icon className="h-3 w-3" /> {label}
            </p>
            <p className="mt-1 truncate text-sm font-medium text-ink-800">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
