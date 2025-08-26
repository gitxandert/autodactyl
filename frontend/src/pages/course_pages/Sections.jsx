import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { useApi } from "../../api/useApi.jsx";
import Card from "../../components/Card.jsx";
import AnimatedElement from "../../utils/AnimatedElement.tsx";

export default function Sections({ selectedId = null }) {
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

   const selected = sections.find((s) => String(s.id) === String(selectedId)) ?? null
   const others = sections.filter((s) => String(s.id) !== String(selectedId)) ?? null

   return (
      <div className="space-y-4">
        {selected ? (
          <>
            <Card title={selected.title} className="sections" style={{ width: '100%', maxWidth: 'none' }}></Card>
          </>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2"> 
            <AnimatePresence>
              {sections.map((s) => (
                <AnimatedElement key={s.id}>
                  <Link to={`/courses/${courseId}/${s.id}`} className="block w-full">
                    <Card title={s.title} className="sections w-full">
                      <p className="text-sm text-muted-foreground">
                        {s.description}
                      </p>
                      <div className="mt-3 text-sm">
                        <span>Lessons: {s.lesson_count}</span>
                      </div>
                    </Card>
                  </Link>
                </AnimatedElement>
              ))}
            </AnimatePresence>
          </div>   
        )}
      </div>
    );     
}
