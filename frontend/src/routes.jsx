import { Routes, Route, Link } from "react-router-dom";

{/* main pages */}
import Home from "./pages/Home.jsx";
import About from "./pages/About.jsx";
import Builder from "./pages/Builder.jsx";
import Community from "./pages/Community.jsx";
import Courses from "./pages/course_pages/Courses.jsx";
import Profile from "./pages/Profile.jsx";

{/* Courses pages */}
import Sections from "./pages/course_pages/Sections.jsx";
import Lessons from "./pages/course_pages/Lessons.jsx";

export default function AppRoutes() {
  return (
    <div className="min-h-screen flex">
      {/* Routed content */}
      <main className="flex-1 p-4 overflow-auto">
        <Routes>
          {/* main routes */}
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/builder" element={<Builder />} />
          <Route path="/community" element={<Community />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/profile" element={<Profile />} />
          
          {/* Courses routes */}
          <Route path="/sections/:courseId" element={<Sections />} />
          <Route path="/lessons/:courseId/:sectionId" element={<Lessons />} />

          {/* default route */}
          <Route index element={<Home  />} />
        </Routes>
      </main>
    </div>
  );
}

