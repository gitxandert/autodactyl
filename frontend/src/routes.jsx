import { Routes, Route } from "react-router-dom";

{/* main pages */}
import Home from "./pages/Home.jsx";
import About from "./pages/About.jsx";
import Builder from "./pages/Builder.jsx";
import Community from "./pages/Community.jsx";
import CourseShell from "./pages/course_pages/CourseShell.jsx";
import SectionShell from "./pages/course_pages/SectionShell.jsx";
import Profile from "./pages/Profile.jsx";

{/* Courses pages */}
import Courses from "./pages/course_pages/Courses.jsx";
import Sections from "./pages/course_pages/Sections.jsx";
import Lessons from "./pages/course_pages/Lessons.jsx";

export default function AppRoutes() {
  return (
    <div>
      {/* Routed content */}
      <main>
        <Routes>
          {/* main routes */}
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/builder" element={<Builder />} />
          <Route path="/community" element={<Community />} />
          <Route path="/profile" element={<Profile />} />
          
          {/* Courses routes (mounted via shell) */}
          <Route path="/courses" element={<CourseShell />} >
            <Route index element={<div />} />
            <Route path=":courseId" element={<SectionShell />} >
              <Route index element={<div />} />
              <Route path=":sectionId" element={<Lessons />} />
            </Route>
          </Route>

          {/* default route */}
          <Route index element={<Home  />} />
        </Routes>
      </main>
    </div>
  );
}

