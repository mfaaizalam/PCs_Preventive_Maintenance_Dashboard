import { useEffect } from "react";
import { NavLink } from "react-router-dom";
import { LayoutGrid, FolderKanban, ClipboardCheck, BarChart3, MonitorCog, UserCircle2 } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutGrid, end: true },
  { to: "/maintenance", label: "Maintenance", icon: ClipboardCheck },
  { to: "/maintenance-overview", label: "Checklist Overview", icon: BarChart3 },
];

export default function Sidebar({ open, onClose }) {
  const { user } = useAuth();

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

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
        className={`fixed inset-y-0 left-0 z-40 flex w-64 max-w-[85vw] flex-col border-r border-ink-100 bg-white transition-transform lg:sticky lg:top-0 lg:h-screen lg:shrink-0 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="hidden h-16 shrink-0 items-center gap-2 border-b border-ink-100 px-5 lg:flex">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-white">
              <MonitorCog className="h-4.5 w-4.5" strokeWidth={2} />
            </div>
            <div className="leading-tight">
              <p className="font-display text-[15px] font-semibold text-ink-900">Lab Monitor</p>
              <p className="text-[11px] text-ink-400">Preventive Maintenance</p>
            </div>
          </div>
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

        <div className="shrink-0 border-t border-ink-100 px-5 py-4">
          {user && (
            <div className="mb-3 flex items-center gap-2.5 sm:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-white">
              <MonitorCog className="h-4.5 w-4.5" strokeWidth={2} />
            </div>
              <div className="min-w-0 leading-tight">

              <p className="text-[11px] text-ink-400">Signed in as</p>
              <p className="truncate text-sm font-medium text-ink-800">
                  {user.name || user.username}
              </p>
              </div>
            </div>
          )}
          <p className="text-[11px] leading-relaxed text-ink-300">
            Preventive Maintenance Dashboard v1.0.0
          </p>
        </div>
      </aside>
    </>
  );
}