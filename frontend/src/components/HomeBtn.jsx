import React from "react";
import { Link } from "react-router-dom";

export default function HomeBtn() {
   return (
     <Link to="/">
       <button className="homeBtn">Home</button>
     </Link>
   );
}
