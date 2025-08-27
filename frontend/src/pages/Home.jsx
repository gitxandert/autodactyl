import React    from "react";
import { Link } from "react-router-dom";

export default function Home() {
   function tintChange(color) {
     document.body.style.setProperty("--tint", color);
   }

   return (
      <div className="main">
         <Link to="/about">
            <button 
               className="mainButton-About"
               onClick={() => tintChange("rgba(255, 50, 255, .5)")}
            >
              About
            </button>
         </Link>
         <Link to="/builder">
             <button 
               className="mainButton-Builder"
               onClick={() => tintChange("rgba(50, 255, 50, .5)")}
             >
               Builder
             </button>
         </Link>
         <Link to="/community">
            <button
              className="mainButton-Community"
              onClick={() => tintChange("rgba(255, 255, 50, .5)")}
            >
              Community
            </button>
         </Link>
         <Link to="/courses">
            <button 
              className="mainButton-Courses"
              onClick={() => tintChange("rgba(50, 50, 255, .5)")}
            >
              Courses
            </button>
         </Link>
         <Link to="/profile">
            <button 
              className="mainButton-Profile"
              onClick={() => tintChange("rgba(255, 50, 50, .5)")}
            >
              Profile
            </button>
         </Link>
      </div>
   )
}
