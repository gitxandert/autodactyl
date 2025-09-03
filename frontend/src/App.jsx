import "./App.css";
import { BrowserRouter as Router } from "react-router-dom";
import { useEffect, useState } from "react";
import AppRoutes from "./routes.jsx";
import LogIn from "./pages/LogIn.jsx";

export default function App() {
  const [isAuthed, setIsAuthed] = useState(false);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/me", { credentials: "include" })
      .then(r => setIsAuthed(r.ok))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return null;
  
  return isAuthed ? (
    <Router>
      <AppRoutes />
    </Router>
  ) : (
    <LogIn
      onSuccess={() => 
        setIsAuthed(true)
      }
    />
  );
}
