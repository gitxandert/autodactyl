import { useEffect, useState } from "react";
import { useApi } from "../api/useApi.jsx";
import Card from "../components/Card.jsx";

export default function Courses() {
   const { listCourses } = useApi();
   const [courses, setCourses] = useState([]);
   const [error, setError] = useState(null);

   useEffect(() => {
      (async () => {
         try {
            const data = await listCourses();
            setCourses(data);
         } catch (e) {
            setError(e.message);
         }
      })();
   }, [listCourses]);

   if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

   return (
      <div className="grid gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
         {courses.map((c) => (
            <Card key={c.id} title={c.title}>
               <p className="text-sm text-muted-foreground">
                  {c.description}
               </p>
               <div className="mt-3 text-sm">
                  <span className="mr-4">Sections: {c.section_count}</span>
                  <span>Lessons: {c.lesson_count}</span>
               </div>
            </Card>
         ))}
      </div>     
   );     
}
