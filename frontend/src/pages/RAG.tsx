import React, { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import ErrorAlert from "../components/ErrorAlert";

export default function RAGPage() {
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [chunks, setChunks] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // connectivity check
    let mounted = true;
    async function check() {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1"}/rag/query`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({ query: "health check", top_k: 1 }),
        });
        if (!mounted) return;
        setEnabled(res.ok);
      } catch {
        if (!mounted) return;
        setEnabled(false);
      }
    }
    check();
    return () => {
      mounted = false;
    };
  }, []);

  async function submitQuery(e?: React.FormEvent) {
    e?.preventDefault();
    setError(null);
    try {
      const res = await apiFetch("/rag/query", {
        method: "POST",
        body: JSON.stringify({ query, top_k: 10 }),
      });
      setAnswer(res.answer);
      setConfidence(res.confidence ?? null);
      setSources(res.sources ?? []);
      setChunks(res.retrieved_chunks ?? []);
    } catch (err: any) {
      setError(String(err));
    }
  }

  async function upload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append("files", file);
      const token = localStorage.getItem("access_token") || "";
      const url = `${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1"}/rag/upload`;
      const res = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      const contentType = res.headers.get("content-type") || "";
      let payload: any = null;
      if (contentType.includes("application/json")) {
        payload = await res.json();
      } else {
        payload = await res.text();
      }
      if (!res.ok) {
        console.error("Upload failed", res.status, payload);
        throw new Error(typeof payload === "string" ? payload : JSON.stringify(payload));
      }
      // success
      setFile(null);
      setAnswer(null);
      setSources([]);
      setChunks([]);
      setError(`Uploaded ${payload?.ingested_chunks ?? "?"} chunks`);
    } catch (err: any) {
      setError(String(err));
    } finally {
      setUploading(false);
    }
  }

  const role = user?.role ?? "anonymous";
  const roleLower = String(role).toLowerCase();
  const canUpload = roleLower === "admin" || roleLower.includes("admin") || roleLower === "hr";

  return (
    <div style={{ maxWidth: 980, margin: 20, fontFamily: "Inter, Arial, sans-serif" }}>
      <h1 style={{ marginBottom: 8 }}>Knowledge Assistant</h1>
      {!enabled && <div style={{ color: "#c00" }}>Knowledge Assistant service unavailable.</div>}
      {enabled && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 20 }}>
          <section className="card">
            <h3 style={{ marginTop: 0 }}>Ask a question</h3>
            <form onSubmit={submitQuery} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter your question" rows={4} />
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <button type="submit">Ask</button>
                <div style={{ marginLeft: "auto", alignSelf: "center" }}>
                  {/* Confidence value kept internally; percentage display removed per UX requirement */}
                </div>
              </div>
            </form>

            {error && <div style={{ marginTop: 8 }}><ErrorAlert title="⚠️ Error" message={error} /></div>}

            {answer && (
              <div style={{ marginTop: 12 }}>
                <h4>Answer</h4>
                <div style={{ background: "#fafafa", padding: 12, borderRadius: 6 }}>{answer}</div>
                <h5 style={{ marginTop: 12 }}>Sources</h5>
                <ul>
                  {sources.map((s, idx) => (
                    <li key={idx}>
                      {s.source} {s.score != null ? <span style={{ color: "var(--muted)" }}>— {Number(s.score).toFixed(2)}</span> : null}
                    </li>
                  ))}
                </ul>
                <details style={{ marginTop: 8 }}>
                  <summary>Retrieved chunks ({chunks.length})</summary>
                  <ul>
                    {chunks.map((c: any) => (
                      <li key={c.id}>
                        <strong>{c.metadata?.source}</strong>: {c.text.slice(0, 400)}
                        {c.text.length > 400 ? "..." : ""}
                      </li>
                    ))}
                  </ul>
                </details>
              </div>
            )}
          </section>

          <aside className="card">
            <h4 style={{ marginTop: 0 }}>Upload Documents</h4>
            {canUpload ? (
              <form onSubmit={upload} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
                <button type="submit" disabled={uploading} className={uploading ? "secondary-btn" : ""}>
                  {uploading ? "Uploading..." : "Upload"}
                </button>
              </form>
            ) : (
              <div>Upload available to Admins only.</div>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}
