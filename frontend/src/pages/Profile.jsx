import React, { useEffect } from "react";
import HomeBtn from "../components/HomeBtn.jsx";

export default function Profile() {
   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(255, 50, 50, .5)");
   })

  return (
    <HomeBtn />
  );
}
