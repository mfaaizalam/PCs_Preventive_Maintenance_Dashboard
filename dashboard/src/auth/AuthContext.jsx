import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { USERS } from "./users";
import { authApi } from "../api/auth";
import { TOKEN_STORAGE_KEY } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  // Restore the session on reload by validating the saved token
  // against the backend (client.js interceptor attaches it).
  useEffect(() => {
    let cancelled = false;

    async function restore() {
      const token = localStorage.getItem(TOKEN_STORAGE_KEY);
      if (!token) {
        setReady(true);
        return;
      }
      try {
        const me = await authApi.me();
        if (!cancelled) {
          const match = USERS.find((u) => u.id === me.role) ?? { id: me.role, name: me.role };
          setUser({ ...match, ...me });
        }
      } catch {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setReady(true);
      }
    }

    restore();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (userId, password) => {
    try {
      const result = await authApi.login(userId, password); // { access_token, role }
      localStorage.setItem(TOKEN_STORAGE_KEY, result.access_token);
      const me = await authApi.me();
      const match = USERS.find((u) => u.id === me.role) ?? { id: me.role, name: me.role };
      setUser({ ...match, ...me });
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err.message || "Wrong password. Try again." };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setUser(null);
  }, []);

  const changePassword = useCallback(async (oldPassword, newPassword) => {
    try {
      await authApi.changePassword(oldPassword, newPassword);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err.message || "Could not change password" };
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, logout, changePassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}