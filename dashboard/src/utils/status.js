// Maps backend ComputerStatus enum values to display tokens.
// Backend source of truth: backend/app/models/enums.py:ComputerStatus

export const STATUS_META = {
  healthy: {
    label: "Healthy",
    dot: "bg-signal-healthy",
    text: "text-signal-healthy",
    bg: "bg-signal-healthyBg",
    ring: "ring-signal-healthy/20",
    border: "border-l-signal-healthy",
  },
  attention: {
    label: "Needs Attention",
    dot: "bg-signal-attention",
    text: "text-signal-attention",
    bg: "bg-signal-attentionBg",
    ring: "ring-signal-attention/20",
    border: "border-l-signal-attention",
  },
  critical: {
    label: "Critical",
    dot: "bg-signal-critical",
    text: "text-signal-critical",
    bg: "bg-signal-criticalBg",
    ring: "ring-signal-critical/20",
    border: "border-l-signal-critical",
  },
  offline: {
    label: "Offline",
    dot: "bg-signal-offline",
    text: "text-signal-offline",
    bg: "bg-signal-offlineBg",
    ring: "ring-signal-offline/20",
    border: "border-l-signal-offline",
  },
  unknown: {
    label: "Unknown",
    dot: "bg-signal-offline",
    text: "text-signal-offline",
    bg: "bg-signal-offlineBg",
    ring: "ring-signal-offline/20",
    border: "border-l-ink-300",
  },
};

export function statusMeta(status) {
  return STATUS_META[status] || STATUS_META.unknown;
}

// A computer counts as "offline" for display purposes if is_online is
// false, regardless of what `status` says (status can lag last_seen).
export function effectiveStatus(computer) {
  if (!computer.is_online) return "offline";
  return computer.status || "unknown";
}

export const ALERT_SEVERITY_META = {
  critical: { label: "Critical", text: "text-signal-critical", bg: "bg-signal-criticalBg" },
  warning: { label: "Warning", text: "text-signal-attention", bg: "bg-signal-attentionBg" },
  info: { label: "Info", text: "text-brand-600", bg: "bg-brand-50" },
};

export function alertSeverityMeta(severity) {
  return ALERT_SEVERITY_META[severity] || ALERT_SEVERITY_META.info;
}

export const ALERT_TYPE_LABEL = {
  performance: "Performance",
  security: "Security",
  license: "License",
  hardware: "Hardware",
  connectivity: "Connectivity",
  maintenance: "Maintenance",
  inventory: "Inventory",
};

export const METRIC_THRESHOLDS = {
  cpu: { warning: 80, critical: 95 },
  ram: { warning: 85, critical: 95 },
  disk: { warning: 85, critical: 95 },
};

export function metricLevel(kind, value) {
  if (value === null || value === undefined) return "unknown";
  const t = METRIC_THRESHOLDS[kind];
  if (value >= t.critical) return "critical";
  if (value >= t.warning) return "attention";
  return "healthy";
}
