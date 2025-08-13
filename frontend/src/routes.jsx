import { Routes, Route, Link } from "react-router-dom";
import About from "./pages/About.jsx";
import Builder from "./pages/Builder.jsx";
import Community from "./pages/Community.jsx";
import Courses from "./pages/Courses.jsx";
import Profile from "./pages/Profile.jsx";

export default function AppRoutes() {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar nav */}
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
      

      {/* Routed content */}
      <main className="flex-1 p-4 overflow-auto">
        <Routes>
          <Route path="/about" element={<About />} />
          <Route path="/builder" element={<Builder />} />
          <Route path="/community" element={<Community />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/profile" element={<Profile />} />
          {/* Optional: default route */}
          <Route index element={<About />} />
        </Routes>
      </main>
    </div>
  );
}

