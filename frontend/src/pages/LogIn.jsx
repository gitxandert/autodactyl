import { useEffect, useState } from "react";

export default function LogIn({ onSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError   ] = useState("");
  const [register, setRegister] = useState(false);
  const [success,  setSuccess ] = useState(false);

  async function verifyReturningUser(e) {
    e.preventDefault();
    setError("");
    const r = await fetch("http://localhost:8000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });
    if (r.ok) onSuccess();
    else setError("Invalid username or password");
  }

  async function registerNewUser(e) {
    e.preventDefault();
    setError("");
    const r = await fetch("http://localhost:8000/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });
    if (r.ok) setSuccess("true");
    else setError("Username already exists");
  }

  useEffect(() => {
    if (success) {
      setRegister(false);
    }
  }, [success]);

  async function handleSubmit(e) {
    if (register) {
      registerNewUser(e);
    }
    else {
      verifyReturningUser(e);
    }
  }

  return (
    <div>
    {success && <div>Successfully registered account! Try logging in.</div>}
    <form onSubmit={handleSubmit}>
      <input className="loginInput" type="username" value={username} onChange={e => setUsername(e.target.value)} />
      <input className="loginInput" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button className="loginBtn" type="submit">{register ? "Register" : "Log In"}</button>
      {error && <div role="alert" style={{ color: "rgb(255, 0, 0)" }}>{error}</div>}
    </form>
    <div style={{ cursor: "pointer", color: "rgb(205, 115, 40)" }} onClick={() => setRegister(!register)}>{register ? "Return to log in" : "New user"}</div>
    </div>
  );
}
