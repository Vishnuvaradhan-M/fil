import React from "react";

export default function ErrorAlert({ title, message }: { title?: string; message: string }) {
  return (
    <div style={{ background: "#fff4f0", borderLeft: "4px solid #f39b6b", padding: 12, borderRadius: 8, color: "#7a2a1d", marginBottom: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{title ?? "⚠️ Something went wrong"}</div>
      <div style={{ color: "#5b2b20", fontSize: 14 }}>{message}</div>
    </div>
  );
}

