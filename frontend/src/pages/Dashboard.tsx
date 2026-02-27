import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

const features = [
  { id: "appointments", label: "Appointments", route: "/appointments", icon: "📅", sub: "Manage appointments" },
  { id: "rooms", label: "Rooms", route: "/rooms", icon: "🛏️", sub: "Manage rooms & capacity" },
  { id: "shifts", label: "Shifts", route: "/shifts", icon: "👥", sub: "Staff schedules" },
  { id: "users", label: "Users", route: "/users", icon: "🧑‍⚕️", sub: "User management" },
  { id: "ml", label: "Clinical Demand & Staffing", route: "/ml", icon: "📈", sub: "Forecasts & optimization" },
  { id: "rag", label: "Knowledge Assistant", route: "/rag", icon: "🔎", sub: "Clinical & Operational Guidelines" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const name = user?.email ? user.email.split("@")[0] : "User";
  const [currentDate, setCurrentDate] = useState<string>(() =>
    new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" })
  );
  const [currentTime, setCurrentTime] = useState<string>(() =>
    new Date().toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false })
  );

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setCurrentDate(now.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" }));
      setCurrentTime(now.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return (
    <div style={{ maxWidth: 1200, margin: "24px auto", fontFamily: "Inter, Arial, sans-serif" }}>
      {/* Vision Quote — TOP */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 18 }}>
        <div className="vision-card">
          <div className="quote-mark">“</div>
          <div style={{ textAlign: "center", position: "relative", zIndex: 2, display: "flex", alignItems: "center", justifyContent: "center", gap: 18 }}>
            <svg className="vision-icon" width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
              <rect x="3" y="3" width="18" height="18" rx="3" fill="#D32F2F" opacity="0.18"/>
              <path d="M12 7v4" stroke="#D32F2F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M10 9h4" stroke="#D32F2F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--deep)", lineHeight: 1.25 }}>Efficiency in operations ensures excellence in patient care.</div>
              <div style={{ marginTop: 12, color: "var(--muted-2)" }}>Hospital Workflow Automation System</div>
              <div style={{ marginTop: 8, color: "var(--muted)" }}>Empowering clinical coordination through data intelligence.</div>
            </div>
            <svg className="vision-icon" width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
              <rect x="3" y="3" width="18" height="18" rx="3" fill="#D32F2F" opacity="0.18"/>
              <path d="M12 7v4" stroke="#D32F2F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M10 9h4" stroke="#D32F2F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="vision-watermark" aria-hidden>🏥</div>
        </div>
      </div>

      {/* Today's Operational Focus — MIDDLE */}
      <div style={{ marginBottom: 18 }}>
        <div className="op-focus-card">
          <div>
            {/* title removed - keeping only date and time per request */}
            <div style={{ marginTop: 8, color: "var(--muted)" }}>
              <div>Date: <span style={{ fontWeight: 600, color: "var(--deep)", marginLeft: 6 }}>{currentDate}</span></div>
            </div>
            {/* description removed per request */}
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, justifyContent: "flex-end" }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 7v5l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
              <div className="clock" style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace", fontSize: 24, fontWeight: 700, color: "var(--deep)" }}>{currentTime}</div>
            </div>
            {/* system status removed per request */}
          </div>
        </div>
      </div>

      {/* Welcome + Feature Cards — LAST */}
      <div className="dashboard-header" style={{ marginBottom: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>Welcome back, {name}</h2>
          <div style={{ color: "var(--muted)", marginTop: 8 }}>
            Manage hospital operations, optimize staffing, and access clinical & operational guidelines.
          </div>
        </div>
      </div>

      <div className="dashboard-grid" style={{ marginBottom: 12 }}>
        {features.map((f) => (
          <Link key={f.id} to={f.route} style={{ textDecoration: "none" }}>
            <div className="feature-card enhanced">
              <div className="feature-icon" aria-hidden>
                {f.icon}
              </div>
              <div className="feature-label">{f.label}</div>
              <div className="feature-sub">{f.sub}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
