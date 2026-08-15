import { Bell, Info } from "lucide-react";
import { alertSeverityMeta, ALERT_TYPE_LABEL } from "../../utils/status";
import { formatDateTime } from "../../utils/format";
import EmptyState from "../common/EmptyState";

export default function PCAlertsSection({ alerts, limited }) {
  return (
    <div className="panel p-5 sm:p-6">
      <h2 className="font-display text-sm font-semibold text-ink-900">Alerts for this PC</h2>

      {limited && (
        <p className="mt-1.5 flex items-start gap-1.5 text-[12px] text-ink-400">
          <Info className="mt-0.5 h-3 w-3 shrink-0" />
          Pulled from the shared dashboard feed, which returns only the 10 most recent unresolved
          alerts system-wide — older or resolved alerts for this PC won't appear here until a
          per-PC alerts endpoint exists.
        </p>
      )}

      {alerts.length === 0 ? (
        <div className="mt-4">
          <EmptyState icon={Bell} title="No active alerts for this PC" />
        </div>
      ) : (
        <ul className="mt-4 divide-y divide-ink-100">
          {alerts.map((alert) => {
            const sev = alertSeverityMeta(alert.severity);
            return (
              <li key={alert.id} className="flex items-start gap-3 py-3">
                <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${sev.text.replace("text-", "bg-")}`} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink-800">{alert.title}</p>
                  <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-[12px] text-ink-400">
                    <span className={`font-medium ${sev.text}`}>{sev.label}</span>
                    <span>·</span>
                    <span>{ALERT_TYPE_LABEL[alert.alert_type] || alert.alert_type}</span>
                    <span>·</span>
                    <span>{formatDateTime(alert.created_at)}</span>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
