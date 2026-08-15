import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { USERS } from "./users";

const STORAGE_KEY = "pm-dashboard.session-user-id";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  // Restore the session on reload so ticking a checklist item
  // doesn't require logging in again every time the tab refreshes.
  useEffect(() => {
    const savedId = localStorage.getItem(STORAGE_KEY);
    if (savedId) {
      const match = USERS.find((u) => u.id === savedId);
      if (match) setUser(match);
    }
    setReady(true);
  }, []);

  const login = useCallback((userId, pin) => {
    const match = USERS.find((u) => u.id === userId);
    if (!match || match.pin !== pin) {
      return { ok: false, error: "Wrong PIN. Try again." };
    }
    localStorage.setItem(STORAGE_KEY, match.id);
    setUser(match);
    return { ok: true };
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}