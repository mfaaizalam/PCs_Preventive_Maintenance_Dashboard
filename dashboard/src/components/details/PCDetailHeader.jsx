import { useState } from "react";
import { ArrowLeft, Tag, Network, MapPin, Cpu, Power } from "lucide-react";
import { Link } from "react-router-dom";
import StatusBadge from "../common/StatusBadge";
import ConfirmDialog from "../common/ConfirmDialog";
import { effectiveStatus } from "../../utils/status";
import { formatDateTime, formatUptime } from "../../utils/format";
import { shutdownComputer, cancelComputerShutdown } from "../../api/computersApi";
import { useAuth } from "../../auth/AuthContext";

export default function PCDetailHeader({ computer, onRefresh }) {
  const status = effectiveStatus(computer);
  const { user } = useAuth();
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handleConfirmShutdown() {
    setBusy(true);
    try {
      await shutdownComputer(computer.id, user?.name ?? "Dashboard");
      await onRefresh?.();
    } finally {
      setBusy(false);
    }
  }

  async function handleCancelShutdown() {
    setBusy(true);
    try {
      await cancelComputerShutdown(computer.id);
      await onRefresh?.();
    } finally {
      setBusy(false);
    }
  }

  const facts = [
    { icon: Tag, label: "Asset ID", value: computer.asset_id || "—" },
    { icon: Network, label: "IP Address", value: computer.ip_address || "—" },
    { icon: MapPin, label: "Location", value: [computer.lab_name, computer.lab_section].filter(Boolean).join(" · ") || "—" },
    { icon: Cpu, label: "OS", value: [computer.os_name, computer.os_version].filter(Boolean).join(" ") || "—" },
  ];

  return (
    <div className="panel p-5 sm:p-6">
      <ConfirmDialog
        open={confirmOpen}
        tone="danger"
        title={`Shut down ${computer.hostname}?`}
        description="This flags the PC to power off on its next check-in (within ~10-60s), after Windows' own shutdown warning. Anyone using it right now will see that warning first."
        confirmLabel="Shut down"
        onConfirm={handleConfirmShutdown}
        onClose={() => setConfirmOpen(false)}
      />

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
            {computer.pending_shutdown && (
              <span className="inline-flex items-center gap-1 rounded-full bg-signal-criticalBg px-2 py-0.5 text-[11px] font-semibold text-signal-critical">
                <Power className="h-3 w-3" /> Shutdown pending
              </span>
            )}
          </div>
          <p className="mt-1.5 text-sm text-ink-400">
            Agent ID <span className="font-mono text-ink-500">{computer.agent_id}</span> ·{" "}
            {computer.is_online ? "Online" : "Offline"} · last check-in{" "}
            {formatDateTime(computer.last_seen)}
            {computer.uptime_seconds != null && ` · up ${formatUptime(computer.uptime_seconds)}`}
          </p>
        </div>

        {computer.is_online && (
          computer.pending_shutdown ? (
            <button
              onClick={handleCancelShutdown}
              disabled={busy}
              className="inline-flex items-center gap-1.5 rounded-lg border border-signal-critical/30 bg-signal-criticalBg px-3.5 py-2 text-sm font-medium text-signal-critical hover:bg-signal-critical/10 disabled:opacity-60"
            >
              <Power className="h-4 w-4" /> Cancel shutdown
            </button>
          ) : (
            <button
              onClick={() => setConfirmOpen(true)}
              disabled={busy}
              className="inline-flex items-center gap-1.5 rounded-lg border border-ink-200 px-3.5 py-2 text-sm font-medium text-ink-600 hover:border-signal-critical/30 hover:text-signal-critical disabled:opacity-60"
            >
              <Power className="h-4 w-4" /> Shut down
            </button>
          )
        )}
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