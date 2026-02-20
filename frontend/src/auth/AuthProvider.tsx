import React, { createContext, useContext, useState, useEffect } from "react";
import { postFormUrlEncoded, apiFetch } from "../api/client";

type User = { email: string; role: string };

const AuthContext = createContext<any>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const email = localStorage.getItem("user_email");
    const role = localStorage.getItem("user_role");
    if (token && email && role) {
      setUser({ email, role });
    }
  }, []);

  async function login(email: string, password: string) {
    const resp = await postFormUrlEncoded("/login/access-token", {
      username: email,
      password,
    });
    localStorage.setItem("access_token", resp.access_token);
    // Call an endpoint to fetch current user details
    const me = await apiFetch("/users/?skip=0&limit=1", { auth: true }).catch(() => null);
    // Try to set basic info
    localStorage.setItem("user_email", email);
    if (Array.isArray(me) && me.length > 0) {
      localStorage.setItem("user_role", me[0].role.toLowerCase());
      setUser({ email, role: me[0].role.toLowerCase() });
    } else {
      // fallback
      localStorage.setItem("user_role", "staff");
      setUser({ email, role: "staff" });
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

