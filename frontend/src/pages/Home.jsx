import { Link } from "react-router-dom";
import About from "./About.jsx";
import Builder from "./Builder.jsx";
import Community from "./Community.jsx";
import Course from "./course_pages/Courses.jsx";
import Profile from "./Profile.jsx";

export default function Home() {
   return (
      <div>
         <Link to="/about">
            <button>About</button>
         </Link>
         <Link to="/builder">
            <button>Builder</button>
         </Link>
         <Link to="/community">
            <button>Community</button>
         </Link>
         <Link to="/courses">
            <button>Courses</button>
         </Link>
         <Link to="/profile">
            <button>Profile</button>
         </Link>
      </div>
   )
}
