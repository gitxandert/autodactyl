import { Outlet, useParams } from "react-router-dom";
import Sections from "./Sections.jsx";

export default function SectionShell() {
  const { sectionId } = useParams();
  return (
    <div className="grid gap-4 p-4 lg:grid-cols-3">
      <div> 
        <Sections selectedId={sectionId ?? null} />
      </div>

      {sectionId && (
        <div>
          <Outlet />
        </div>
      )}
    </div>
  );
}
