// Browser-visible demonstration settings; these do not implement server authentication.
export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

export const demoCredentials = {
  employee: {
    user: import.meta.env.VITE_DEMO_EMPLOYEE_USER ?? "",
    pass: import.meta.env.VITE_DEMO_EMPLOYEE_PASSWORD ?? "",
  },
  admin: {
    user: import.meta.env.VITE_DEMO_ADMIN_USER ?? "",
    pass: import.meta.env.VITE_DEMO_ADMIN_PASSWORD ?? "",
  },
};
