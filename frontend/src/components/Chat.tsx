import React, { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useApi } from "../api/useApi.jsx";

export type ChatMessage = {
  id:       string;
  role:     "user" | "assistant" | "system";
  content:  string;
  status?:  int;
  body_md?: string;
};

export type ChatProps = {
  /* specify if "build", "learn", etc. */
  purpose:          string;
  /* unique for every chat */
  sessionId:        string;
  /* fixed height of the scroll area (px) */
  height?:          number;
  /* placeholder text for the input */
  placeholder?:     string;
  /* disable input/buttons while an in-flight request is pending */
  disabled?:        boolean;
  /* optional initial history to seed the transcript */
  initialMessages?: ChatMessage[] | string | null | undefined;
  /* called after a successful reply is received */
  onReply?:         (reply: ChatMessage, all: ChatMessage[], server: any) => void;
  /* allows for extra controls in the footer (e.g., Approve & Save) */
  footerExtras?:    React.ReactNode;
  /* used for Lesson chat */
  specialBtn?:     boolean;
  specialMess?:     string;
};

function typeMessage(
  fullText: string,
  baseMsg: ChatMessage,
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>,
  speed = 30 // ms per character
) {
  let i = 0;

  // Add initial empty assistant message
  setMessages((prev) => [...prev, { ...baseMsg, content: "" }]);

  const interval = setInterval(() => {
    i++;
    setMessages((prev) => {
      // Update *just* the last assistant message
      const next = [...prev];
      const last = next[next.length - 1];
      if (last.id === baseMsg.id) {
        next[next.length - 1] = { ...last, content: fullText.slice(0, i) };
      }
      return next;
    });

    if (i >= fullText.length) {
      clearInterval(interval);
    }
  }, speed);
}

export default function Chat({
  purpose,
  sessionId,
  height = 260,
  placeholder = "Type a message…",
  initialMessages = [],
  disabled = false,
  onReply,
  footerExtras,
  specialBtn = false,
  specialMess
}: ChatProps) {
  const { LLMchat } = useApi();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [specialMessage, setSpecialMessage] = useState(specialMess);
  const [busy, setBusy] = useState(false);
  const [pendingServer, setPendingServer] = useState<any>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let initial: ChatMessage[] = [];
    if (Array.isArray(initialMessages)) initial = initialMessages;
    else if (typeof initialMessages === "string" && initialMessages.trim()) {
      try { initial = JSON.parse(initialMessages) as ChatMessage[]; } catch {}
  }
    setMessages(initial);
  }, []);

  // Auto-scroll to newest message
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);
  
  const btnStyle = useMemo(
    () => ({
      background: "#2563eb",
      color: "#fff",
      border: 0,
      borderRadius: 8,
      padding: "8px 12px",
      cursor: "pointer" as const,
    }),
    []
  );

  async function send(text="") {
    if (text === "") text = input.trim();
    if (!text || busy || disabled) return;

    const userMsg: ChatMessage = {
      id: `${Date.now()}-u`,
      role: "user",
      content: text,
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setBusy(true);

    try {
      const data = await LLMchat({
         purpose,
         message: text,
         session_id: sessionId,
      });

      if (!data?.ok) throw new Error(data?.error || "Chat failed");
      
      const replyText =
        data?.result?.response ??  "";
      const replyStatus = 
        data?.result?.status ?? null;
      const replyBody_md =
        data?.result?.body_md ?? null;

      const asst: ChatMessage = {
        id: `${Date.now()}-a`,
        role: "assistant",
        content: "", // start empty
      };

      typeMessage(replyText ?? "", asst, setMessages, 25);
      onReply?.(asst, [...messages, asst], data);
      
      if (specialBtn) {
         setSpecialMessage(() => {
            if (replyStatus === 1) {
               if (replyBody_md === "") {
                  return "Finish";
               }
               else {
                  return "Continue";
               }
            }
            else {
               return "Finished";
            }
         })
      }
    } catch (err: any) {
      const errMsg: ChatMessage = {
        id: `${Date.now()}-e`,
        role: "system",
        content: `Error: ${err.message || String(err)}`,
      };
      setMessages((m) => [...m, errMsg]);
    } finally {
      setBusy(false);
    }
  }

  function specialSend() {
    if (specialMessage != "Completed") {
      void send(specialMessage);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      void send();
    }
  }

  const [chatPrompt, setChatPrompt] = useState("");
  
  useEffect(() => {
    if (purpose === "learn") {
      setChatPrompt("ask a question");
    }
    else if (purpose === "build") {
      setChatPrompt("describe your course");
    }
  }, [purpose]);
  
  const target = typeof window !== "undefined" && document.getElementById("continue-top");

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {specialBtn && target ?
          createPortal(
            <button
              onClick={() => void specialSend()}
              disabled={busy || disabled || specialMessage === "finished"}
              style={{
                ...btnStyle,
                background: busy || disabled ? "#9fb7aa" : "#2563eb",
             }}
            >
              {specialMessage}
            </button>, target
          ) : <></>  
       }
       <div
        ref={scrollRef}
        style={{
          height,
          overflow: "auto",
          border: "1px solid #eee",
          borderRadius: 8,
          padding: 10,
          background: "#0c0f45",
        }}
      >
        {messages.length === 0 && (
          <div style={{ opacity: 0.6 }}>No messages yet.</div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} msg={m} />
        ))}

        {busy && (
          <div style={{ opacity: 0.7, fontStyle: "italic", marginTop: 8 }}>
            Assistant is thinking…
          </div>
        )}
      </div>

      <label htmlFor="chat-input" style={{ fontWeight: 600 }}>
        {chatPrompt} 
      </label>
      <textarea
        id="chat-input"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={placeholder}
        style={{
          minHeight: 90,
          marginTop: 4,
          padding: 10,
          borderRadius: 8,
          border: "1px solid #ddd",
          resize: "vertical",
        }}
        disabled={busy || disabled || specialMessage === "Finished"}
        onKeyDown={onKeyDown}
      />

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        {specialBtn ?
          <button
            onClick={() => void specialSend()}
            disabled={busy || disabled || specialMessage === "Finished"}
            style={{
              ...btnStyle,
              background: busy || disabled ? "#9fb7aa" : "#2563eb",
            }}
          >
            {specialMessage}
          </button> : <></>  
        }
        {specialMessage === "Finished" ? <></> :
          <>
            <button
              onClick={() => void send()}
              disabled={busy || disabled || !input.trim()}
              style={{
                ...btnStyle,
                background: busy || disabled || !input.trim() ? "#9fb7aa" : "#2563eb",
              }}
            >
              {busy ? "Thinking…" : "Send"}
            </button>
            <div style={{ fontSize: 12, opacity: 0.7 }}>Tip: Ctrl/Cmd + Enter to send.</div>
          </>
        }
        <div style={{ marginLeft: "auto" }}>{footerExtras}</div>
      </div>
    </div>
  );
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  const isSystem = msg.role === "system";
  const bubbleStyle: React.CSSProperties = {
    display: "flex",
    justifyContent: isUser ? "flex-end" : "flex-start",
    marginBottom: 8,
  };

  const innerStyle: React.CSSProperties = {
    maxWidth: "85%",
    background: isSystem ? "#b0172e" : isUser ? "#43a9f7" : "#7326d1",
    border: "1px solid #eee",
    padding: "8px 10px",
    borderRadius: 10,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    fontSize: 14,
  };

  const labelStyle: React.CSSProperties = {
    fontSize: 11,
    opacity: 0.7,
    marginBottom: 4,
    textTransform: "capitalize",
  };

  return (
    <div style={bubbleStyle}>
      <div style={innerStyle}>
        <div style={labelStyle}>{msg.role}</div>
        <div>{msg.content}</div>
      </div>
    </div>
  );
}
