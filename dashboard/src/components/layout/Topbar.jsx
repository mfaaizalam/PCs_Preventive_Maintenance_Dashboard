import { Menu, Circle, LogOut, UserCircle2 } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";

export default function Topbar({ onMenuClick, connectionOk }) {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-ink-100 bg-white/90 px-4 backdrop-blur sm:px-6">
      <button
        onClick={onMenuClick}
        className="rounded-md p-1.5 text-ink-500 hover:bg-ink-50 lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="hidden lg:block" />

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-full border border-ink-100 bg-ink-50 px-3 py-1.5 text-[12px] font-medium text-ink-500">
          <Circle
            className={`h-2 w-2 ${
              connectionOk ? "fill-signal-healthy text-signal-healthy" : "fill-signal-critical text-signal-critical"
            }`}
          />
          {connectionOk ? "API connected" : "API unreachable"}
        </div>

        {user && (
          <div className="flex items-center gap-2 rounded-full border border-ink-100 bg-ink-50 px-3 py-1.5 text-[12px] font-medium text-ink-600">
            <UserCircle2 className="h-4 w-4 text-ink-400" />
            {user.name}
            <button
              onClick={logout}
              className="ml-1 flex items-center gap-1 rounded-full px-1.5 py-0.5 text-ink-400 hover:bg-white hover:text-ink-700"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}