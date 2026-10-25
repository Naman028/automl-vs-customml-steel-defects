import React, { createContext, useContext, useState, useEffect } from "react";
import { DEMO_MODE, demoCredentials } from "./authConfig";

interface User {
  username: string;
  role: "employee" | "admin" | "demo";
  token: string;
}

interface AuthContextType {
  user: User | null;
  login: (
    username: string,
    password: string,
    role: "employee" | "admin",
  ) => Promise<boolean>;
  loginDemo: () => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (!DEMO_MODE) return;
    // Check for stored auth on mount
    const storedAuth = localStorage.getItem("steel_auth");
    if (storedAuth) {
      try {
        setUser(JSON.parse(storedAuth));
      } catch {
        localStorage.removeItem("steel_auth");
      }
    }
  }, []);

  const login = async (
    username: string,
    password: string,
    role: "employee" | "admin",
  ): Promise<boolean> => {
    if (!DEMO_MODE || !username || !password) return false;
    const validCredentials = demoCredentials;

    if (
      (role === "employee" &&
        username === validCredentials.employee.user &&
        password === validCredentials.employee.pass) ||
      (role === "admin" &&
        username === validCredentials.admin.user &&
        password === validCredentials.admin.pass)
    ) {
      const mockToken = `mock_jwt_${role}_${Date.now()}`;
      const userData = { username, role, token: mockToken };
      setUser(userData);
      localStorage.setItem("steel_auth", JSON.stringify(userData));
      return true;
    }
    return false;
  };

  const loginDemo = () => {
    if (!DEMO_MODE) return;
    const demoUser = {
      username: "Demo User",
      role: "demo" as const,
      token: `mock_jwt_demo_${Date.now()}`,
    };
    setUser(demoUser);
    localStorage.setItem("steel_auth", JSON.stringify(demoUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("steel_auth");
  };

  return (
    <AuthContext.Provider
      value={{ user, login, loginDemo, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
