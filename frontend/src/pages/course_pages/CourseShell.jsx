import { Outlet, useParams } from "react-router-dom";
import Courses from "./Courses.jsx";

export default function CourseShell() {
  const { courseId } = useParams();
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
