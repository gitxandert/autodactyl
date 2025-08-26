import { Outlet, useParams } from "react-router-dom";
import Courses from "./Courses.jsx";

export default function CourseShell() {
  const { courseId } = useParams();
  return (
    <div className="grid gap-4 p-4 lg:grid-cols-3">
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
