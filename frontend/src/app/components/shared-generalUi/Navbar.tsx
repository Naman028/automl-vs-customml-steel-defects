import React from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useTheme } from "../../contexts/ThemeContext";
import {
  Moon,
  Sun,
  LogOut,
  BarChart3,
  Home,
  ShieldCheck,
  User,
} from "lucide-react";
import { Button } from "../ui/button";

interface NavbarProps {
  currentPage: "dashboard" | "comparison";
  onNavigate: (page: "dashboard" | "comparison") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm sticky top-0 z-50 transition-colors duration-300 backdrop-blur-lg bg-white/80 dark:bg-slate-900/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-slate-700 to-slate-900 dark:from-slate-600 dark:to-slate-800 rounded-xl flex items-center justify-center shadow-lg transition-transform hover:scale-110">
              <span className="text-white text-xl">🔍</span>
            </div>
            <div>
              <h1 className="text-xl text-slate-900 dark:text-white tracking-tight">
                Metal Defect AI
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {user?.role === "admin" ? (
                  <span className="flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    Admin Access
                  </span>
                ) : user?.role === "demo" ? (
                  "🎓 Demo Mode"
                ) : (
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    Employee Access
                  </span>
                )}
              </p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-2">
            <Button
              variant={currentPage === "dashboard" ? "default" : "ghost"}
              onClick={() => onNavigate("dashboard")}
              className={
                currentPage === "dashboard"
                  ? "bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 shadow-md"
                  : "hover:bg-slate-100 dark:hover:bg-slate-800"
              }
            >
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
            <Button
              variant={currentPage === "comparison" ? "default" : "ghost"}
              onClick={() => onNavigate("comparison")}
              className={
                currentPage === "comparison"
                  ? "bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 shadow-md"
                  : "hover:bg-slate-100 dark:hover:bg-slate-800"
              }
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Comparison
            </Button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
              aria-label="Toggle theme"
            >
              {theme === "light" ? (
                <Moon className="w-5 h-5 text-slate-600 dark:text-slate-300" />
              ) : (
                <Sun className="w-5 h-5 text-slate-400" />
              )}
            </button>

            {/* User Info & Logout */}
            <div className="flex items-center space-x-2 ml-4 pl-4 border-l border-slate-200 dark:border-slate-700">
              <span className="text-sm text-slate-700 dark:text-slate-300 hidden sm:inline">
                {user?.username}
              </span>
              <Button
                variant="ghost"
                onClick={logout}
                className="text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
