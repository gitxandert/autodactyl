import React, { useEffect, useState } from "react";
import HomeBtn from "../components/HomeBtn.jsx";
import { useApi } from "../api/useApi.jsx";

export default function Profile() {
   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(255, 50, 50, .5)");
   })
  
  const { getUser } = useApi();
  const [info, setInfo] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await getUser();
        setInfo(data);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [getUser]);

  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        maxWidth: '800px',
        margin: '0 auto',
        height: '100vh',
      }}
    >
      <HomeBtn />
      <div className="profile">
        <div type="username" className="profile-name profile-row">
          <strong>Your username:</strong>
          <span>{info.username}</span>
        </div>
        <div type="hiddenPass" className="profile-password profile-row">
          <strong>Your (encrypted) password:</strong>
          <span>*******</span>
        </div>
      </div>
    </div>
  );
}
