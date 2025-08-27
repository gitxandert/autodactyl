import React from "react";
import { Link } from "react-router-dom";

export default function HomeBtn() {
   function tintChange(color) {
     document.body.style.setProperty("--tint", color);
   }

   return (
     <Link to="/">
       <button
         style={{ backgroundColor: 'rgba(50, 255, 255, .7)' }} 
         onClick={() => tintChange("rgba(50, 255, 255, .5)")}
       >
         Home
       </button>
     </Link>
   );
}
