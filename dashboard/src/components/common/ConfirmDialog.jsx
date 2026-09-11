import { AlertTriangle } from "lucide-react";

export default function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  tone = "confirm",
  onConfirm,
  onClose,
}) {
  if (!open) return null;

  const confirmClasses =
    tone === "danger"
      ? "bg-signal-critical text-white hover:bg-signal-critical/90"
      : "bg-brand-700 text-white hover:bg-brand-800";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-ink-900/40" onClick={onClose} aria-hidden="true" />
      <div className="relative w-full max-w-sm rounded-xl2 bg-white p-5 shadow-cardHover">
        <div className="flex items-start gap-3">
          <span
            className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
              tone === "danger" ? "bg-signal-criticalBg text-signal-critical" : "bg-brand-50 text-brand-700"
            }`}
          >
            <AlertTriangle className="h-4.5 w-4.5" />
          </span>
          <div className="min-w-0">
            <h3 className="font-display text-[15px] font-semibold text-ink-900">{title}</h3>
            {description && <p className="mt-1 text-sm text-ink-500">{description}</p>}
          </div>
        </div>

        <div className="mt-5 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="rounded-lg border border-ink-200 px-3.5 py-2 text-sm font-medium text-ink-600 hover:bg-ink-50"
          >
            {tone === "blocked" ? "OK" : "Cancel"}
          </button>
          {tone !== "blocked" && (
            <button
              onClick={() => {
                onConfirm?.();
                onClose?.();
              }}
              className={`rounded-lg px-3.5 py-2 text-sm font-medium transition ${confirmClasses}`}
            >
              {confirmLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}