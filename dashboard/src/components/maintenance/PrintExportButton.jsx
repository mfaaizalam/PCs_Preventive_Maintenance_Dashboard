import { useEffect, useRef, useState } from "react";
import { Printer, Loader2, ChevronDown, Monitor, LayoutGrid } from "lucide-react";
import { downloadChecklistExport } from "../../api/maintenanceApi";

/**
 * Print/export button for the checklist views.
 *
 * - On a single PC's page (computerId + hostname given): opens a small
 *   menu to choose between exporting just this PC, or the whole master
 *   list, for whichever frequency/period tab is currently open.
 * - On the roll-up overview (no computerId): exports the whole master
 *   list directly, no menu needed.
 */
export default function PrintExportButton({ frequency, period, computerId, hostname }) {
  const [open, setOpen] = useState(false);
  const [downloading, setDownloading] = useState(null); // "pc" | "lab" | null
  const [error, setError] = useState(null);
  const menuRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    function onClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  async function runExport(scope) {
    setError(null);
    setDownloading(scope);
    setOpen(false);
    try {
      await downloadChecklistExport({
        frequency,
        period,
        computerId: scope === "pc" ? computerId : undefined,
      });
    } catch (err) {
      setError(err?.message || "Export failed.");
    } finally {
      setDownloading(null);
    }
  }

  const label = frequency
    ? `Print ${frequency.replace("_", " ")} report`
    : "Print report";

  // No single-PC context (e.g. Checklist Overview page) — one direct button.
  if (!computerId) {
    return (
      <div className="flex flex-col items-end gap-1">
        <button
          onClick={() => runExport("lab")}
          disabled={downloading !== null}
          className="inline-flex items-center gap-2 rounded-lg border border-ink-200 bg-white px-3 py-1.5 text-sm font-medium text-ink-700 transition hover:border-brand-400 hover:text-brand-700 disabled:opacity-60"
        >
          {downloading === "lab" ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Printer className="h-4 w-4" />
          )}
          {label}
        </button>
        {error && <p className="text-[11px] text-signal-critical">{error}</p>}
      </div>
    );
  }

  return (
    <div className="relative flex flex-col items-end gap-1" ref={menuRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        disabled={downloading !== null}
        className="inline-flex items-center gap-2 rounded-lg border border-ink-200 bg-white px-3 py-1.5 text-sm font-medium text-ink-700 transition hover:border-brand-400 hover:text-brand-700 disabled:opacity-60"
      >
        {downloading !== null ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Printer className="h-4 w-4" />
        )}
        {label}
        <ChevronDown className={`h-3.5 w-3.5 transition ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute right-0 top-[calc(100%+6px)] z-10 w-64 overflow-hidden rounded-xl2 border border-ink-100 bg-white shadow-cardHover">
          <button
            onClick={() => runExport("pc")}
            className="flex w-full items-start gap-2.5 px-4 py-3 text-left transition hover:bg-ink-50"
          >
            <Monitor className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" />
            <span>
              <span className="block text-sm font-medium text-ink-800">This PC</span>
              <span className="block text-[12px] text-ink-400">
                {hostname || "Just this computer"}'s checklist only
              </span>
            </span>
          </button>
          <div className="h-px bg-ink-100" />
          <button
            onClick={() => runExport("lab")}
            className="flex w-full items-start gap-2.5 px-4 py-3 text-left transition hover:bg-ink-50"
          >
            <LayoutGrid className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" />
            <span>
              <span className="block text-sm font-medium text-ink-800">All PCs (master list)</span>
              <span className="block text-[12px] text-ink-400">Every enrolled PC, grouped by lab</span>
            </span>
          </button>
        </div>
      )}
      {error && <p className="text-[11px] text-signal-critical">{error}</p>}
    </div>
  );
}
