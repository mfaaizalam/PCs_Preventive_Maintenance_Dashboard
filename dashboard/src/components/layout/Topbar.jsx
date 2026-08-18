import { Menu, Circle, LogOut, UserCircle2 } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import NotificationBell from "../common/NotificationBell";

export default function Topbar({ onMenuClick, connectionOk }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between border-b border-ink-100 bg-white px-4 py-3 sm:px-6">
      <button
        onClick={onMenuClick}
        className="rounded-md p-1.5 text-ink-500 hover:bg-ink-50 lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex flex-1 items-center justify-end gap-3">
        <div className="flex items-center gap-1.5 text-[12px] font-medium text-ink-400">
          <Circle
            className={`h-2 w-2 ${connectionOk ? "fill-signal-healthy text-signal-healthy" : "fill-signal-critical text-signal-critical"}`}
          />
          {connectionOk ? "API connected" : "API unreachable"}
        </div>

        <NotificationBell />

        {user && (
          <div className="flex items-center gap-2">
            <UserCircle2 className="h-5 w-5 text-ink-400" />
            <span className="text-sm text-ink-600">{user.username || user.email}</span>
            <button
              onClick={logout}
              className="rounded-md p-1.5 text-ink-400 hover:bg-ink-50 hover:text-ink-700"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}