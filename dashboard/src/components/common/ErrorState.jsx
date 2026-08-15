import { AlertOctagon, RotateCw, WifiOff } from "lucide-react";

// The URL shown in the network-error message: in dev this is what
// vite.config.js proxies /api and /health to; in prod it describes
// wherever the reverse proxy in front of this app should be routing
// those same paths.
const BACKEND_TARGET = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function ErrorState({ error, onRetry, compact = false }) {
  const isNetwork = error?.isNetworkError;

  return (
    <div
      className={`flex flex-col items-center justify-center gap-3 rounded-xl2 border border-ink-100 bg-white text-center ${
        compact ? "py-10" : "py-20"
      }`}
    >
      {isNetwork ? (
        <WifiOff className="h-8 w-8 text-signal-critical" strokeWidth={1.6} />
      ) : (
        <AlertOctagon className="h-8 w-8 text-signal-critical" strokeWidth={1.6} />
      )}
      <div className="max-w-sm px-6">
        <p className="text-sm font-medium text-ink-800">
          {isNetwork ? "Can't reach the backend API" : "The request failed"}
        </p>
        <p className="mt-1 text-sm text-ink-500">
          {isNetwork
            ? `No response reaching ${BACKEND_TARGET} (via the /api proxy). Confirm the FastAPI server is running and VITE_API_BASE_URL is set correctly.`
            : error?.message || "An unexpected error occurred."}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-1 inline-flex items-center gap-1.5 rounded-lg border border-ink-200 bg-white px-3.5 py-1.5 text-sm font-medium text-ink-700 shadow-panel transition hover:border-brand-300 hover:text-brand-700"
        >
          <RotateCw className="h-3.5 w-3.5" />
          Try again
        </button>
      )}
    </div>
  );
}
