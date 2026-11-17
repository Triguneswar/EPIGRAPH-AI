import { Outlet } from "react-router-dom";

export default function ProtectedRoute() {
  // Direct access without login
  return <Outlet />;
}
