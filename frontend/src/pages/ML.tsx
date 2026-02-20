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
    <div>
      <h1>ML - Forecast</h1>
      <label>Date</label>
      <input value={date} onChange={(e) => setDate(e.target.value)} placeholder="YYYY-MM-DD" />
      <label>Hour</label>
      <input type="number" value={hour} onChange={(e) => setHour(Number(e.target.value))} />
      <button onClick={forecast}>Forecast</button>
      {error && <div className="error">{error}</div>}
      {result && (
        <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result, null, 2)}</pre>
      )}
      <hr />
      <h2>Shift Optimize</h2>
      <input placeholder="Date (YYYY-MM-DD)" value={optDate} onChange={(e) => setOptDate(e.target.value)} />
      <input type="number" value={optHour} onChange={(e) => setOptHour(Number(e.target.value))} />
      <button onClick={optimize}>Optimize</button>
      {optResult && (
        <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(optResult, null, 2)}</pre>
      )}
    </div>
  );
}

