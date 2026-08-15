import { Link } from "react-router-dom";
import { MonitorX } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-24 text-center">
      <MonitorX className="h-9 w-9 text-ink-300" strokeWidth={1.6} />
      <p className="font-display text-lg font-semibold text-ink-800">Page not found</p>
      <p className="max-w-sm text-sm text-ink-400">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <Link
        to="/"
        className="mt-2 rounded-lg bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-800"
      >
        Back to dashboard
      </Link>
    </div>
  );
}
