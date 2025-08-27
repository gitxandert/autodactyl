import React, { useEffect } from "react";
import HomeBtn from "../components/HomeBtn.jsx";

export default function About() {
   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(205, 50,  205, .7)");
   })

  return (
    <HomeBtn />
  );
}
