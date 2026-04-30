import { Navigate, Outlet } from "react-router-dom";
import { getStoredToken } from "../api/auth";

export function ProtectedRoute() {
  if (!getStoredToken()) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
