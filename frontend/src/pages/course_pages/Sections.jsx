import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Home from "../Home.jsx";
import Courses from "./Courses.jsx";
import { useApi } from "../../api/useApi.jsx";
import Card from "../../components/Card.jsx";

export default function Sections() {
   const { courseId: cidString } = useParams();

   // Parse safely; undefined -> NaN
   const parsed = Number.parseInt(cidString ?? "", 10);

   // show if id is wrong type
   if (!Number.isInteger(parsed) || parsed <= 0) {
     return <div>Invalid course id: {cidString}</div>
   }

   const courseId = parsed;

   const { listSections } = useApi();
   const [sections, setSections] = useState([]);
   const [error, setError] = useState(null);

   useEffect(() => {
      (async () => {
         try {
            const data = await listSections(courseId);
            setSections(data);
         } catch (e) {
            setError(e.message);
         }
      })();
   }, [listSections]);

   if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

   return (
      <div className="grid gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
        
         <Link to="/courses"><button>Courses</button></Link>
         <Link to="/"><button>Home</button></Link>

         {sections.map((s) => (
            <Card key={s.id} title={s.title}>
               <p className="text-sm text-muted-foreground">
                  {s.description}
               </p>
               <div className="mt-3 text-sm">
                  <span>Lessons: {s.lesson_count}</span>
               </div>
            </Card>
         ))}
      </div>     
   );     
}
