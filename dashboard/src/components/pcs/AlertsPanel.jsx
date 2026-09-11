import { useState } from "react";
import { Link } from "react-router-dom";
import { Bell, ChevronRight, AlertOctagon, AlertTriangle, Info, X, Loader2 } from "lucide-react";
import { alertSeverityMeta, ALERT_TYPE_LABEL } from "../../utils/status";
import { formatRelativeTime } from "../../utils/format";
import EmptyState from "../common/EmptyState";

const SEVERITY_ICON = {
  critical: AlertOctagon,
  warning: AlertTriangle,
  info: Info,
};

const SEVERITY_BORDER = {
  critical: "border-l-signal-critical",
  warning: "border-l-signal-attention",
  info: "border-l-brand-500",
};

export default function AlertsPanel({ alerts, computersById, onDismiss }) {
  const [dismissing, setDismissing] = useState(null);

  async function handleDismiss(e, alertId) {
    e.preventDefault();
    e.stopPropagation();
    setDismissing(alertId);
    try {
      await onDismiss?.(alertId);
    } finally {
      setDismissing(null);
    }
  }

  return (
    <div className="panel flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-ink-100 px-4 py-3.5">
        <h3 className="font-display text-sm font-semibold text-ink-900">Recent Alerts</h3>
        <span className="eyebrow">{alerts.length}</span>
      </div>

      {alerts.length === 0 ? (
        <div className="flex-1 p-4">
          <EmptyState icon={Bell} title="No active alerts" description="All monitored PCs are within normal thresholds." />
        </div>
      ) : (
        <ul className="max-h-[420px] flex-1 space-y-2 overflow-y-auto p-3">
          {alerts.map((alert) => {
            const sev = alertSeverityMeta(alert.severity);
            const Icon = SEVERITY_ICON[alert.severity] || Info;
            const borderClass = SEVERITY_BORDER[alert.severity] || SEVERITY_BORDER.info;
            const computer = alert.computer_id != null ? computersById[alert.computer_id] : null;
            const isDismissing = dismissing === alert.id;

            const content = (
              <div
                className={`relative flex items-start gap-3 rounded-lg border-l-4 ${borderClass} ${sev.bg} px-3.5 py-3 pr-9`}
              >
                <Icon className={`mt-0.5 h-4.5 w-4.5 shrink-0 ${sev.text}`} />
                <div className="min-w-0 flex-1">
                  <p className={`text-sm font-semibold ${sev.text}`}>{sev.label}</p>
                  <p className="mt-0.5 truncate text-sm font-medium text-ink-800">{alert.title}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-x-2 text-[12px] text-ink-500">
                    <span>{ALERT_TYPE_LABEL[alert.alert_type] || alert.alert_type}</span>
                    {computer && (
                      <>
                        <span>·</span>
                        <span className="truncate">{computer.hostname}</span>
                      </>
                    )}
                    <span>·</span>
                    <span>{formatRelativeTime(alert.created_at)}</span>
                  </div>
                </div>
                {computer && <ChevronRight className="mt-1 h-4 w-4 shrink-0 text-ink-300" />}

                <button
                  onClick={(e) => handleDismiss(e, alert.id)}
                  disabled={isDismissing}
                  aria-label="Dismiss alert"
                  title="Dismiss"
                  className="absolute right-2 top-2 rounded-full p-1 text-ink-400 hover:bg-white/60 hover:text-ink-700 disabled:opacity-50"
                >
                  {isDismissing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <X className="h-3.5 w-3.5" />}
                </button>
              </div>
            );

            return (
              <li key={alert.id}>
                {computer ? (
                  <Link to={`/pcs/${encodeURIComponent(computer.agent_id)}`} className="block transition hover:opacity-90">
                    {content}
                  </Link>
                ) : (
                  content
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}