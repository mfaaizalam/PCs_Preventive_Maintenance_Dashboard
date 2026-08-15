import { Link } from "react-router-dom";
import { Bell, ChevronRight } from "lucide-react";
import { alertSeverityMeta, ALERT_TYPE_LABEL } from "../../utils/status";
import { formatRelativeTime } from "../../utils/format";
import EmptyState from "../common/EmptyState";

export default function AlertsPanel({ alerts, computersById }) {
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
        <ul className="max-h-[420px] flex-1 divide-y divide-ink-100 overflow-y-auto">
          {alerts.map((alert) => {
            const sev = alertSeverityMeta(alert.severity);
            const computer = alert.computer_id != null ? computersById[alert.computer_id] : null;
            const content = (
              <div className="flex items-start gap-3 px-4 py-3">
                <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${sev.bg}`}>
                  <span className={`block h-2 w-2 rounded-full ${sev.text.replace("text-", "bg-")}`} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-ink-800">{alert.title}</p>
                  <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-[12px] text-ink-400">
                    <span className={`font-medium ${sev.text}`}>{sev.label}</span>
                    <span>·</span>
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
              </div>
            );

            return (
              <li key={alert.id}>
                {computer ? (
                  <Link
                    to={`/pcs/${encodeURIComponent(computer.agent_id)}`}
                    className="block transition hover:bg-ink-50"
                  >
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
