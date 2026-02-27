import React, { useState } from "react";
import { apiFetch } from "../api/client";

export default function MlPage() {
  const [date, setDate] = useState("");
  const [hour, setHour] = useState(9);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [optDate, setOptDate] = useState("");
  const [optHour, setOptHour] = useState(9);
  const [optResult, setOptResult] = useState<any>(null);

  async function optimize() {
    setError(null);
    try {
      const resp = await apiFetch("/ml/shift-optimize", { method: "POST", body: JSON.stringify({ date: optDate, hour: optHour }) });
      setOptResult(resp);
    } catch (e: any) {
      setError(String(e));
    }
  }

  async function forecast() {
    setError(null);
    try {
      const resp = await apiFetch("/ml/forecast", {
        method: "POST",
        body: JSON.stringify({ date, hour }),
      });
      setResult(resp);
    } catch (e: any) {
      setError(String(e));
    }
  }

  return (
    <div style={{ maxWidth: 1100, margin: "24px auto", fontFamily: "Inter, Arial, sans-serif", color: "#222" }}>
      <h1 style={{ marginBottom: 8 }}>Clinical Demand & Staffing</h1>
      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ background: "#fff", padding: 20, borderRadius: 10, boxShadow: "0 2px 8px rgba(16,24,40,0.04)" }}>
          <h3 style={{ marginTop: 0 }}>Forecast</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
            <input type="number" value={hour} onChange={(e) => setHour(Number(e.target.value))} style={{ width: 100 }} />
            <button onClick={forecast}>Forecast</button>
          </div>
          {error && <div style={{ color: "#c00", marginTop: 8 }}>{error}</div>}
          {result && (
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: "#0b63c6" }}>{Math.round(result.predicted_demand ?? 0)}</div>
              <div style={{ color: "#666", marginTop: 8, fontSize: 14 }}>
                Predicted demand (rounded)
              </div>
              <div style={{ marginTop: 12 }}>
                <strong>Features used</strong>
                <ul style={{ marginTop: 8, lineHeight: 1.6 }}>
                  <li>Doctor count: {result.features_used?.doctor_count ?? "-"}</li>
                  <li>Emergency count: {result.features_used?.emergency_count ?? "-"}</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        <div style={{ background: "#fff", padding: 20, borderRadius: 10, boxShadow: "0 2px 8px rgba(16,24,40,0.04)" }}>
          <h3 style={{ marginTop: 0 }}>Shift Optimize</h3>
            <div style={{ display: "flex", gap: 8 }}>
            <input type="date" placeholder="Date" value={optDate} onChange={(e) => setOptDate(e.target.value)} />
            <input type="number" value={optHour} onChange={(e) => setOptHour(Number(e.target.value))} style={{ width: 100 }} />
            <button onClick={optimize}>Optimize</button>
          </div>
          {optResult && (
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: "#0b63c6" }}>Predicted demand: {Math.round(optResult.predicted_demand ?? 0)}</div>
              <div style={{ marginTop: 8 }}>Recommended staff count: <strong>{optResult.recommended_staff_count ?? 0}</strong></div>
              <div style={{ marginTop: 12 }}>
                <strong>Recommended staff (priority)</strong>
                <ul style={{ marginTop: 8, lineHeight: 1.6 }}>
                  {(optResult.priority_order || []).map((name: string, i: number) => (
                    <li key={i}>
                      {name} — current assignments: {optResult.staff_details?.[i]?.current_assignments ?? 0}
                    </li>
                  ))}
                </ul>
              </div>
              <div style={{ marginTop: 8, padding: 10, background: "#f7f7f7", borderRadius: 6 }}>
                {optResult.recommendation_text}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

