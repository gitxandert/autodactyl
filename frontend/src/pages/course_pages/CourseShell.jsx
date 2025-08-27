import React, { useEffect } from "react";
import { Outlet, useParams } from "react-router-dom";
import Courses from "./Courses.jsx";

export default function CourseShell() {
  const { courseId } = useParams();

   useEffect(() => {
     document.body.style.setProperty("--tint", "rgba(50, 50, 255, .5)");
   })

  return (
    <div>
      <div>
        <Courses selectedId={courseId ?? null} />
      </div>

      {courseId && (
        <div>
          <Outlet />
        </div>
      )}
    </div>
  );
}
