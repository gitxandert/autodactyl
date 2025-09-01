import React, { useEffect, useState }    from "react";
import { Link } from "react-router-dom";
import LogIn from "./LogIn.jsx";

export default function Home() {
   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(50, 255, 255, .5)");
   })
   
   const [showLogIn, setShowLogIn] = useState(false); 

   useEffect(() => {
     let sid = localStorage.getItem("auto_session_id");
     if (!sid) {
       setShowLogIn(true);
     }
     else {
       setShowLogIn(false);
     }
   }, []);

   return (
      <div>
      {showLogIn ? (
         <LogIn />
      ) : (
      <div className="main">
         <img className="logo" src="/autodactyl.svg" alt="autodactyl logo" />
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
      )}
      </div>
   )
}
