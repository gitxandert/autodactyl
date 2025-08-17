import { Link } from "react-router-dom";
import About from "./About.jsx";
import Builder from "./Builder.jsx";
import Community from "./Community.jsx";
import Course from "./course_pages/Courses.jsx";
import Profile from "./Profile.jsx";

export default function Home() {
   return (
      <div className="main">
         <Link to="/about" className="mainButton-About">
            <button>About</button>
         </Link>
         <Link to="/builder" className="mainButton-Builder">
             <button>Builder</button>
         </Link>
         <Link to="/community" className="mainButton-Community">
            <button>Community</button>
         </Link>
         <Link to="/courses" className="mainButton-Courses">
            <button>Courses</button>
         </Link>
         <Link to="/profile" className="mainButton-Profile">
            <button>Profile</button>
         </Link>
      </div>
   )
}
