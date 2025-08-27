import { Outlet, useParams } from "react-router-dom";
import Sections from "./Sections.jsx";

export default function SectionShell() {
  const { sectionId } = useParams();
  return (
    <div>
      <div className="min-w-0"> 
        <Sections selectedId={sectionId ?? null} />
      </div>

      {sectionId && (
        <div className="min-w-0">
          <Outlet />
        </div>
      )}
    </div>
  );
}
