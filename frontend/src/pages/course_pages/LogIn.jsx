function useSessionId(key = "auto_session_id") {
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


export default function LogIn() {
  const sessionId = useSessionId();
  return ();
}
