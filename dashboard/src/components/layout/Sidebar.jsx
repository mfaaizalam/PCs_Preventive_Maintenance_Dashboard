import { NavLink } from "react-router-dom";
import { LayoutGrid, FolderKanban, ClipboardCheck, BarChart3, MonitorCog, X } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutGrid, end: true },
  { to: "/categories", label: "Categories", icon: FolderKanban },
  { to: "/maintenance", label: "Maintenance", icon: ClipboardCheck },
  { to: "/maintenance-overview", label: "Checklist Overview", icon: BarChart3 },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-ink-950/40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-ink-100 bg-white transition-transform lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between gap-2 border-b border-ink-100 px-5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-white">
              <MonitorCog className="h-4.5 w-4.5" strokeWidth={2} />
            </div>
            <div className="leading-tight">
              <p className="font-display text-[15px] font-semibold text-ink-900">Lab Monitor</p>
              <p className="text-[11px] text-ink-400">Preventive Maintenance</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-ink-400 hover:bg-ink-50 lg:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-50 text-brand-800"
                    : "text-ink-500 hover:bg-ink-50 hover:text-ink-800"
                }`
              }
            >
              <Icon className="h-4.5 w-4.5" strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-ink-100 px-5 py-4">
          <p className="text-[11px] leading-relaxed text-ink-300">
            Asset &amp; preventive-maintenance tracking for department lab PCs.
          </p>
        </div>
      </aside>
    </>
  );
}