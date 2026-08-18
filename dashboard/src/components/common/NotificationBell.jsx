import { useState } from "react";
import { Link } from "react-router-dom";
import { Bell, X, MonitorX } from "lucide-react";
import useHardwareNotifications from "../../hooks/useHardwareNotifications";
import { formatDateTime } from "../../utils/format";
import EmptyState from "./EmptyState";

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const { notifications, unreadCount, markAllSeen } = useHardwareNotifications();

  const handleOpen = () => {
    setOpen(true);
    markAllSeen();
  };

  return (
    <>
      <button
        onClick={handleOpen}
        className="relative rounded-full border border-ink-100 bg-ink-50 p-2 text-ink-500 hover:bg-ink-100 hover:text-ink-700"
        aria-label="Hardware notifications"
        title="Hardware notifications (last 24h)"
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-signal-critical px-1 text-[10px] font-semibold leading-none text-white">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="fixed inset-0 z-40 flex justify-end">
          <div
            className="absolute inset-0 bg-ink-900/30"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <div className="relative flex h-full w-full max-w-sm flex-col bg-white shadow-cardHover">
            <div className="flex items-center justify-between border-b border-ink-100 px-4 py-3.5">
              <div>
                <h3 className="font-display text-sm font-semibold text-ink-900">
                  Hardware Notifications
                </h3>
                <p className="text-[12px] text-ink-400">Last 24 hours</p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="rounded-md p-1.5 text-ink-400 hover:bg-ink-50 hover:text-ink-700"
                aria-label="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {notifications.length === 0 ? (
              <div className="flex-1 p-4">
                <EmptyState
                  icon={MonitorX}
                  title="No hardware removals"
                  description="No mouse, keyboard, or USB removals in the last 24 hours."
                />
              </div>
            ) : (
              <ul className="flex-1 divide-y divide-ink-100 overflow-y-auto">
                {notifications.map((n) => (
                  <li key={n.id} className="px-4 py-3">
                    <Link
                      to={`/pcs/${encodeURIComponent(n.agent_id)}`}
                      onClick={() => setOpen(false)}
                      className="block hover:opacity-80"
                    >
                      <p className="text-sm font-medium text-ink-800">
                        {n.hostname} — {n.message}
                      </p>
                      <p className="mt-0.5 text-[12px] text-ink-400">
                        {formatDateTime(n.occurred_at)}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </>
  );
}