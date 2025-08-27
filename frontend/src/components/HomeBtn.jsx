import React from "react";
import { Link } from "react-router-dom";

export default function HomeBtn() {
   return (
     <Link to="/">
       <button
         style={{ backgroundColor: 'rgba(30, 235, 235, .7)' }} 
       >
         Home
       </button>
     </Link>
   );
}
