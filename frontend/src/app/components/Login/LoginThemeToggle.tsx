import React from "react";
import { Moon, Sun } from "lucide-react";

type LoginThemeToggleProps = {
  theme: "light" | "dark";
  onToggle: () => void;
};

export const LoginThemeToggle: React.FC<LoginThemeToggleProps> = ({
  theme,
  onToggle,
}) => {
  return (
    <button
      onClick={onToggle}
      className="fixed top-6 right-6 p-3 rounded-xl bg-white dark:bg-slate-800 shadow-lg hover:shadow-xl transition-all duration-200 border border-slate-200 dark:border-slate-700"
      aria-label="Toggle theme"
    >
      {theme === "light" ? (
        <Moon className="w-5 h-5 text-slate-700" />
      ) : (
        <Sun className="w-5 h-5 text-slate-300" />
      )}
    </button>
  );
};
