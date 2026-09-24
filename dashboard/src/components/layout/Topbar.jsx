import { useState } from "react";
import { Menu, Circle, LogOut, UserCircle2, KeyRound, MonitorCog } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import NotificationBell from "../common/NotificationBell";
import ChangePasswordModal from "../auth/ChangePasswordModal";

export default function Topbar({ onMenuClick, connectionOk, menuOpen = false }) {
  const { user, logout } = useAuth();
  const [showChangePassword, setShowChangePassword] = useState(false);
  const userLabel = user ? user.name || user.username : "";

  return (
    <header className="flex h-16 items-center justify-between gap-3 border-b border-ink-100 bg-white px-4 sm:px-6">
      {!menuOpen && (
        <div className="flex min-w-0 items-center gap-2.5 lg:hidden">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-700 text-white">
            <MonitorCog className="h-4.5 w-4.5" strokeWidth={2} />
          </div>
          <div className="min-w-0 leading-tight">
            <p className="truncate font-display text-[15px] font-semibold text-ink-900">Lab Monitor</p>
            <p className="hidden truncate text-[11px] text-ink-400 min-[420px]:block">
              Preventive Maintenance
            </p>
          </div>
        </div>
      )}

      <div className="ml-auto flex shrink-0 items-center gap-1.5 sm:gap-3">
        <div
          className="flex items-center gap-1.5 text-[12px] font-medium text-ink-400"
          title={connectionOk ? "API connected" : "API unreachable"}
        >
          <Circle
            className={`h-2 w-2 ${connectionOk ? "fill-signal-healthy text-signal-healthy" : "fill-signal-critical text-signal-critical"}`}
          />
          <span className="hidden sm:inline">
            {connectionOk ? "API connected" : "API unreachable"}
          </span>
          <span className="sr-only sm:hidden">
            {connectionOk ? "API connected" : "API unreachable"}
          </span>
        </div>

        <NotificationBell />

        {user && (
          <div className="flex items-center gap-1 sm:gap-2">
            <UserCircle2 className="h-5 w-5 shrink-0 text-ink-400" title={userLabel} />
            <span className="hidden max-w-[10rem] truncate text-sm text-ink-600 sm:inline">
              {userLabel}
            </span>

            <button
              onClick={() => setShowChangePassword(true)}
              className="rounded-md p-1.5 text-ink-400 hover:bg-ink-50 hover:text-ink-700"
              aria-label="Change password"
              title="Change password"
            >
              <KeyRound className="h-4 w-4" />
            </button>

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

        <button
          onClick={onMenuClick}
          className="rounded-md p-1.5 text-ink-500 hover:bg-ink-50 lg:hidden"
          aria-label="Open menu"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>

      <ChangePasswordModal
        open={showChangePassword}
        onClose={() => setShowChangePassword(false)}
      />
    </header>
  );
}