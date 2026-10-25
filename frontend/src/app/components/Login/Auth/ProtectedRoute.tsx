import React from "react";
import { useAuth } from "../../../contexts/AuthContext";
import { Login } from "../Login";
import { DEMO_MODE } from "../../../contexts/authConfig";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (DEMO_MODE && !isAuthenticated) {
    return <Login />;
  }

  return <>{children}</>;
};
