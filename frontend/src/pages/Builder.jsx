import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useApi } from "../api/useApi.jsx";
import Home from "./Home.jsx";
import Courses from "./course_pages/Courses.jsx";
import Chat from "../components/Chat.tsx";

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

export default function Builder() {
   const navigate = useNavigate();
   const sessionId = useSessionId();
   const { LLMchat, approveCourse } = useApi();
   const [input, setInput] = useState("");
   const [busy, setBusy] = useState(false);
   const [log, setLog] = useState([]); // {role: 'user'|'system', text}
   const [draft, setDraft] = useState(null); // whatever your backend returns as draft
   const outRef = useRef(null);

   useEffect(() => {
      if (outRef.current) outRef.current.scrollTop = outRef.current.scrollHeight;
   }, [log, draft]);

   const canApprove = useMemo(() => !!draft, [draft]);

   async function approve() {
      if (!canApprove) return;
      setBusy(true);
      try {
         const data = await approveCourse(sessionId);
         if (!data.ok) throw new Error(data.error || "Approval failed");
         navigate("/courses");
      } catch (e) {
         console.error(e);
      } finally {
         setBusy(false);
      }
   }

   return(
      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 24 }}>
         <div>
            <Link to="/"><button>Home</button></Link>
            <h2 style={{ fontSize: 18, marginBottom: 8 }}>Chat</h2>
            <div>
               <Chat
                purpose={"build"}
                sessionId={sessionId}
                disabled={!sessionId}
                height={260}
                footerExtras={(
                  <button onClick={approve} disabled={!canApprove || busy} style={{ background: canApprove && !busy ? "#0b8457" : "#9fb7aa", color: "#fff", border: 0, borderRadius: 8, padding: "8px 12px" }}>
                     Approve & Save
                  </button>
                )}
                onReply={(_, __, server) => {
                   // try to find a draft/course in the server payload
                  const result = server?.result ?? server;
                  const maybeDraft =
                    result?.draft ??
                    result?.course ??
                    result?.data?.draft ??
                    result?.data?.course ??
                    null;
              
                  if (maybeDraft) setDraft(maybeDraft);
                }}
                />
            </div>
         </div>
         <div>
            <h2 style={{ fontSize: 18, marginBottom: 8 }}>Current Draft</h2>
            <pre style={{ height: 260, overflow: "auto", border: "1px solid #eee", borderRadius: 8, padding: 10, background: "#111", color: "#e6e6e6" }}>
               {draft ? pretty(draft) : "—"}
            </pre>
         </div>
      </section>
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

