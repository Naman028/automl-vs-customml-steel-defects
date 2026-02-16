import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useTheme } from "../../contexts/ThemeContext";
import { LoginBrandingPanel } from "./LoginBrandingPanel";
import { LoginFormCard } from "./LoginFormCard";
import { LoginThemeToggle } from "./LoginThemeToggle";

export const Login: React.FC = () => {
  const { login, loginDemo } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [role, setRole] = useState<"employee" | "admin">("employee");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const success = await login(username, password, role);

    if (!success) {
      setError("Invalid credentials. Try: employee/REMOVED_DEMO_CREDENTIAL or admin/REMOVED_DEMO_CREDENTIAL");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-slate-50 to-white dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-300">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-slate-200/30 dark:bg-slate-700/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-slate-200/30 dark:bg-slate-700/20 rounded-full blur-3xl"></div>
      </div>

      <LoginThemeToggle theme={theme} onToggle={toggleTheme} />

      <div className="relative w-full max-w-6xl mx-4 grid md:grid-cols-2 gap-8">
        <LoginBrandingPanel />
        <LoginFormCard
          role={role}
          username={username}
          password={password}
          error={error}
          loading={loading}
          onRoleChange={setRole}
          onUsernameChange={setUsername}
          onPasswordChange={setPassword}
          onSubmit={handleLogin}
          onDemoLogin={loginDemo}
        />
      </div>
    </div>
  );
};
