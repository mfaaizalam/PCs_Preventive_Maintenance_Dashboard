import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { MonitorCog, Lock } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { USERS } from "../auth/users";

export default function Login() {
  const { user, login } = useAuth();
  const location = useLocation();
  const [userId, setUserId] = useState(USERS[0].id);
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");

  if (user) {
    const redirectTo = location.state?.from ?? "/";
    return <Navigate to={redirectTo} replace />;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const result = login(userId, pin);
    if (!result.ok) {
      setError(result.error);
      setPin("");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-50 px-4">
      <div className="w-full max-w-sm rounded-xl2 bg-white p-6 shadow-cardHover">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-700 text-white">
            <MonitorCog className="h-5 w-5" strokeWidth={2} />
          </div>
          <div className="leading-tight">
            <p className="font-display text-[15px] font-semibold text-ink-900">Lab Monitor</p>
            <p className="text-[11px] text-ink-400">Sign in to continue</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-[12px] font-medium text-ink-500">Who are you?</label>
            <select
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-ink-200 bg-white px-3 py-2 text-sm text-ink-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
            >
              {USERS.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[12px] font-medium text-ink-500">PIN</label>
            <div className="relative mt-1">
              <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-300" />
              <input
                autoFocus
                type="password"
                inputMode="numeric"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                placeholder="••••"
                className="w-full rounded-lg border border-ink-200 bg-white py-2 pl-9 pr-3 text-sm text-ink-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
              />
            </div>
          </div>

          {error && <p className="text-sm text-signal-critical">{error}</p>}

          <button
            type="submit"
            className="w-full rounded-lg bg-brand-700 px-3.5 py-2 text-sm font-medium text-white hover:bg-brand-800"
          >
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
}