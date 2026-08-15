import { Monitor, CheckCircle2, AlertTriangle, XCircle, WifiOff, Bell } from "lucide-react";

function StatCard({ icon: Icon, label, value, tone }) {
  return (
    <div className="panel flex items-center gap-3 px-4 py-3.5">
      <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${tone.bg}`}>
        <Icon className={`h-4.5 w-4.5 ${tone.text}`} strokeWidth={2} />
      </div>
      <div>
        <p className="font-mono text-lg font-semibold leading-none text-ink-900">{value}</p>
        <p className="mt-1 text-[12px] text-ink-400">{label}</p>
      </div>
    </div>
  );
}

export default function StatStrip({ overview }) {
  if (!overview) return null;

  const stats = [
    { icon: Monitor, label: "Total PCs", value: overview.total_pcs, tone: { bg: "bg-brand-50", text: "text-brand-700" } },
    { icon: CheckCircle2, label: "Healthy", value: overview.healthy_count, tone: { bg: "bg-signal-healthyBg", text: "text-signal-healthy" } },
    { icon: AlertTriangle, label: "Attention", value: overview.attention_count, tone: { bg: "bg-signal-attentionBg", text: "text-signal-attention" } },
    { icon: XCircle, label: "Critical", value: overview.critical_count, tone: { bg: "bg-signal-criticalBg", text: "text-signal-critical" } },
    { icon: WifiOff, label: "Offline", value: overview.offline_count, tone: { bg: "bg-signal-offlineBg", text: "text-signal-offline" } },
    { icon: Bell, label: "Active alerts", value: overview.active_alert_count, tone: { bg: "bg-ink-100", text: "text-ink-600" } },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {stats.map((s) => (
        <StatCard key={s.label} {...s} />
      ))}
    </div>
  );
}
