import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function NavBar() {
  const { user, logout } = useAuth();
  const [showRag, setShowRag] = React.useState(false);

  React.useEffect(() => {
    let mounted = true;
    async function check() {
      if (!user) {
        setShowRag(false);
        return;
      }
      const roleLower = String(user.role).toLowerCase();
      const allowed = ["admin", "hr", "doctor", "staff"];
      if (!allowed.includes(roleLower)) {
        setShowRag(false);
        return;
      }
      try {
        // silent connectivity check (keep intact, do not change API)
        const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1"}/rag/query`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({ query: "health check", top_k: 1 }),
        });
        if (!mounted) return;
        setShowRag(resp.ok);
      } catch {
        if (!mounted) return;
        setShowRag(false);
      }
    }
    check();
    return () => {
      mounted = false;
    };
  }, [user]);

  const nav = useNavigate();
  return (
    <nav className="nav">
      <div className="brand" style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
          <rect x="2" y="4" width="20" height="14" rx="2" stroke="none" fill="currentColor" opacity="0.08" />
          <path d="M12 7v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M9 10h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M6 4v16" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.6"/>
        </svg>
        <Link to="/">Hospital Workflow Automation System</Link>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div className="links" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {user && (
            <>
              <Link to="/shifts">Shifts</Link>
              <Link to="/appointments">Appointments</Link>
              <Link to="/rooms">Rooms</Link>
              <Link to="/ml">Clinical Demand &amp; Staffing</Link>
              {showRag && <Link to="/rag">Knowledge Assistant</Link>}
              {(user.role === "admin" || user.role === "hr") && <Link to="/users">Users</Link>}
            </>
          )}
          {!user && <Link to="/login">Login</Link>}
        </div>

        {user && (
          <div className="user-info">
            <div>
              <div className="user-name">{user.email}</div>
              <div className="user-badge" style={{ textTransform: "capitalize" }}>{user.role}</div>
            </div>
            <button
              onClick={() => {
                logout();
                nav("/login");
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}