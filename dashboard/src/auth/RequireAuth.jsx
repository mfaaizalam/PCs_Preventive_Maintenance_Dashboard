import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import LoadingState from "../components/common/LoadingState";

export default function RequireAuth({ children }) {
  const { user, ready } = useAuth();
  const location = useLocation();

  if (!ready) return <LoadingState label="Loading…" />;
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  return children;
}