import { Loader2 } from "lucide-react";

export default function LoadingState({ label = "Loading…", compact = false }) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-3 text-ink-400 ${
        compact ? "py-8" : "py-24"
      }`}
    >
      <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
      <p className="text-sm">{label}</p>
    </div>
  );
}
