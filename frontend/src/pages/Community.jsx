import React, { useEffect }    from "react";
import HomeBtn from "../components/HomeBtn.jsx";

export default function Community() {
   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(255, 255, 50, .5)");
   })  

  return (
    <HomeBtn />
  );
}
