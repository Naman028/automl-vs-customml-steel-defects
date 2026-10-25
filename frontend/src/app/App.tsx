import React, { useState } from "react";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { PredictionHistoryProvider } from "./contexts/PredictionHistoryContext";
import { ProtectedRoute } from "./components/Login/Auth/ProtectedRoute";
import { Navbar, AppPage } from "./components/shared-generalUi/Navbar";
import { Dashboard } from "./pages/Dashboard";
import { Comparison } from "./pages/Comparison";
import { Gc10Results } from "./pages/Gc10Results";

export default function App() {
  const [currentPage, setCurrentPage] = useState<AppPage>("dashboard");

  return (
    <ThemeProvider>
      <AuthProvider>
        <PredictionHistoryProvider>
          <ProtectedRoute>
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-300">
              <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
              {currentPage === "dashboard" && <Dashboard />}
              {currentPage === "comparison" && <Comparison />}
              {currentPage === "gc10" && <Gc10Results />}
            </div>
          </ProtectedRoute>
        </PredictionHistoryProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
