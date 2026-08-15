import { AlertTriangle, CheckCircle2, WifiOff, XCircle, HelpCircle } from "lucide-react";
import { statusMeta } from "../../utils/status";

const ICONS = {
  healthy: CheckCircle2,
  attention: AlertTriangle,
  critical: XCircle,
  offline: WifiOff,
  unknown: HelpCircle,
};

export default function StatusBadge({ status, size = "md" }) {
  const meta = statusMeta(status);
  const Icon = ICONS[status] || HelpCircle;
  const sizing = size === "sm" ? "text-[11px] px-2 py-0.5 gap-1" : "text-xs px-2.5 py-1 gap-1.5";

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizing} ${meta.bg} ${meta.text}`}
    >
      <Icon className={size === "sm" ? "h-3 w-3" : "h-3.5 w-3.5"} strokeWidth={2.4} />
      {meta.label}
    </span>
  );
}
