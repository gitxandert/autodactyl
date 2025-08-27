import React, { useEffect }    from "react";
import { Link } from "react-router-dom";

export default function Home() {
   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(50, 255, 255, .5)");
   })

   return (
      <div className="main">
         <img src="/autodactyl.svg" alt="autodactyl logo" />
         <div className="mainButtons">
           <Link to="/about">
             <button 
              className="mainButton-About"
             >
               About
             </button>
           </Link>
           <Link to="/builder">
             <button 
              className="mainButton-Builder"
             >
               Builder
             </button>
           </Link>
           <Link to="/community">
             <button
              className="mainButton-Community"
             >
               Community
             </button>
           </Link>
           <Link to="/courses">
             <button 
              className="mainButton-Courses"
             >
               Courses
             </button>
           </Link>
           <Link to="/profile">
             <button 
              className="mainButton-Profile"
             >
               Profile
             </button>
           </Link>
        </div>
      </div>
   )
}
