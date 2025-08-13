import React, { useEffect, useMemo, useRef, useState } from "react";
import Home from "./Home.jsx";

function useSessionId(key = "course_session_id") {
  const [sessionId, setSessionId] = useState("");
  useEffect(() => {
    let sid = localStorage.getItem(key);
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem(key, sid);
    }
    setSessionId(sid);
  }, [key]);
  return sessionId;
}

function pretty(obj) {
  try { return JSON.stringify(obj, null, 2); } catch { return String(obj); }
}

const API_BASE = (import.meta?.env?.VITE_API_BASE ?? "").replace(/\/$/, ""); 

export function useApi(base = API_BASE) {
  const buildCourse = async (message, session_id) => {
    const res = await fetch(`${base}/api/build-course`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id }),
    });
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return res.json();
  };

  const approveCourse = async (session_id) => {
    const res = await fetch(`${base}/api/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id }),
    });
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    return res.json();
  };

  return { buildCourse, approveCourse };
}


export default function Builder() {
  const sessionId = useSessionId();
  const { buildCourse, approveCourse } = useApi();
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState([]); // {role: 'user'|'system', text}
  const [draft, setDraft] = useState(null); // whatever your backend returns as draft
  const outRef = useRef(null);

  useEffect(() => {
    if (outRef.current) outRef.current.scrollTop = outRef.current.scrollHeight;
  }, [log, draft]);

  const canApprove = useMemo(() => !!draft, [draft]);

  async function sendMessage() {
    const msg = input.trim();
    if (!msg) return;
    setInput("");
    setLog((l) => [...l, { role: "user", text: msg }]);
    setBusy(true);
    try {
      const data = await buildCourse(msg, sessionId);
      if (!data.ok) throw new Error(data.error || "Request failed");

      const dataResponse = data.result.response;
      setLog((l) => [...l, { role: "system", text: dataResponse }]);
      
      const maybeDraft = data.result?.draft ?? data.result?.course ?? data.result;
      setDraft(maybeDraft);
    } catch (e) {
      setLog((l) => [...l, { role: "system", text: `Error: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function approve() {
    if (!canApprove) return;
    setBusy(true);
    setLog((l) => [...l, { role: "user", text: "Approve" }]);
    try {
      const data = await approveCourse(sessionId);
      if (!data.ok) throw new Error(data.error || "Approval failed");
      setLog((l) => [...l, { role: "system", text: "Approved and saved to DB." }]);
      // Optionally clear draft after approval
      // setDraft(null);
    } catch (e) {
      setLog((l) => [...l, { role: "system", text: `Error: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{
      maxWidth: 960, margin: "2rem auto", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif", padding: "0 1rem"
    }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h1 style={{ fontSize: 28, margin: 0 }}>Course Builder</h1>
        <code style={{ fontSize: 12, opacity: 0.8 }}>session: {sessionId}</code>
      </header>
      
      <Home />

      <section style={{ marginTop: 16 }}>
        <label htmlFor="msg" style={{ fontWeight: 600 }}>Message</label>
        <textarea
          id="msg"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., Create a 4-week course with 2 lessons/week, quizzes on Fridays."
          style={{ width: "100%", minHeight: 100, marginTop: 8, padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) sendMessage(); }}
        />
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <button onClick={sendMessage} disabled={busy} style={btnStyle}>{busy ? "Working…" : "Send"}</button>
          <button onClick={approve} disabled={!canApprove || busy} style={{ ...btnStyle, background: canApprove && !busy ? "#0b8457" : "#9fb7aa" }}>Approve & Save</button>
        </div>
        <p style={{ fontSize: 12, opacity: 0.7, marginTop: 8 }}>Tip: press Ctrl/Cmd + Enter to send.</p>
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 24 }}>
        <div>
          <h2 style={{ fontSize: 18, marginBottom: 8 }}>Activity</h2>
          <div ref={outRef} style={{ height: 260, overflow: "auto", border: "1px solid #eee", borderRadius: 8, padding: 10, background: "#fafafa" }}>
            {log.length === 0 && <div style={{ opacity: 0.6 }}>No messages yet.</div>}
            {log.map((m, i) => (
              <div key={i} style={{ marginBottom: 8 }}>
                <b style={{ textTransform: "capitalize" }}>{m.role}:</b> {m.text}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 style={{ fontSize: 18, marginBottom: 8 }}>Current Draft</h2>
          <pre style={{ height: 260, overflow: "auto", border: "1px solid #eee", borderRadius: 8, padding: 10, background: "#111", color: "#e6e6e6" }}>
            {draft ? pretty(draft) : "—"}
          </pre>
        </div>
      </section>

      <footer style={{ marginTop: 24, fontSize: 12, opacity: 0.75 }}>
        <p>
          Backend base URL is assumed to be <code>http://localhost:8000</code>. If different, change <code>useApi()</code> above.
        </p>
      </footer>
    </div>
  );
}

const btnStyle = {
  appearance: "none",
  border: "none",
  background: "black",
  color: "white",
  padding: "10px 14px",
  borderRadius: 8,
  cursor: "pointer"
};

