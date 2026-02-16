import React from "react";
import { LogIn, ShieldCheck, User } from "lucide-react";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

type LoginFormCardProps = {
  role: "employee" | "admin";
  username: string;
  password: string;
  error: string;
  loading: boolean;
  onRoleChange: (role: "employee" | "admin") => void;
  onUsernameChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onDemoLogin: () => void;
};

export const LoginFormCard: React.FC<LoginFormCardProps> = ({
  role,
  username,
  password,
  error,
  loading,
  onRoleChange,
  onUsernameChange,
  onPasswordChange,
  onSubmit,
  onDemoLogin,
}) => {
  return (
    <div className="flex flex-col justify-center space-y-6">
      <Card className="border-2 border-slate-200 dark:border-slate-700 shadow-2xl dark:bg-slate-900 backdrop-blur-sm">
        <CardHeader className="space-y-1 pb-4">
          <CardTitle className="text-2xl text-center text-slate-900 dark:text-white">
            Sign In
          </CardTitle>
          <CardDescription className="text-center text-slate-600 dark:text-slate-400">
            Choose your role to continue
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => onRoleChange("employee")}
              className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                role === "employee"
                  ? "border-slate-600 bg-slate-50 dark:bg-slate-800 dark:border-slate-500"
                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              }`}
            >
              <User
                className={`w-6 h-6 mx-auto mb-2 ${role === "employee" ? "text-slate-700 dark:text-slate-300" : "text-slate-400"}`}
              />
              <p
                className={`text-sm ${role === "employee" ? "text-slate-900 dark:text-slate-200" : "text-slate-600 dark:text-slate-400"}`}
              >
                Employee
              </p>
            </button>
            <button
              type="button"
              onClick={() => onRoleChange("admin")}
              className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                role === "admin"
                  ? "border-slate-600 bg-slate-50 dark:bg-slate-800 dark:border-slate-500"
                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              }`}
            >
              <ShieldCheck
                className={`w-6 h-6 mx-auto mb-2 ${role === "admin" ? "text-slate-700 dark:text-slate-300" : "text-slate-400"}`}
              />
              <p
                className={`text-sm ${role === "admin" ? "text-slate-900 dark:text-slate-200" : "text-slate-600 dark:text-slate-400"}`}
              >
                Admin
              </p>
            </button>
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label
                htmlFor="username"
                className="text-slate-700 dark:text-slate-300"
              >
                Username
              </Label>
              <Input
                id="username"
                type="text"
                placeholder={role === "employee" ? "employee" : "admin"}
                value={username}
                onChange={(e) => onUsernameChange(e.target.value)}
                required
                className="dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 focus:border-slate-400 dark:focus:border-slate-500"
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="password"
                className="text-slate-700 dark:text-slate-300"
              >
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder={role === "employee" ? "emp123" : "admin123"}
                value={password}
                onChange={(e) => onPasswordChange(e.target.value)}
                required
                className="dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 focus:border-slate-400 dark:focus:border-slate-500"
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800">
                {error}
              </p>
            )}

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-slate-700 to-slate-900 hover:from-slate-800 hover:to-slate-950 dark:from-slate-600 dark:to-slate-800 shadow-lg hover:shadow-xl transition-all"
              disabled={loading}
            >
              {loading ? (
                "Authenticating..."
              ) : (
                <>
                  <LogIn className="w-4 h-4 mr-2" />
                  Sign In as {role === "employee" ? "Employee" : "Admin"}
                </>
              )}
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-slate-300 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white dark:bg-slate-900 px-3 text-slate-500 tracking-wider">
                Or
              </span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full border-2 border-slate-300 dark:border-slate-600 dark:hover:bg-slate-800 hover:bg-slate-50 transition-all"
            onClick={onDemoLogin}
          >
            Faculty Demo Mode (No Auth Required)
          </Button>
        </CardContent>
      </Card>

      <p className="text-center text-xs text-slate-500 dark:text-slate-400">
        Demo credentials: employee/emp123 or admin/admin123
      </p>
    </div>
  );
};
