import { useEffect, useMemo, useState }  from "react";
import { Link }                 from "react-router-dom";
import { AnimatePresence }      from "framer-motion";
import { useApi }               from "../../api/useApi.jsx";
import Card                     from "../../components/Card.tsx";
import AnimatedElement          from "../../utils/AnimatedElement.tsx";

export default function Courses({ selectedId = null }) {
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

   const selected = courses.find((c) => String(c.id) === String(selectedId)) ?? null
   const others = courses.filter((c) => String(c.id) !== String(selectedId)) ?? null

   return (
    <div>
      <Link to="/"><button>Home</button></Link>

      {selected ? (
        <>
          <Link to="/courses"><button>Courses</button></Link>
          <Link to={`/courses/${selected.id}`} className="block">
            <Card title={selected.title} className="courses"></Card>
          </Link>
        </>
      ) : (
        <div>
          <AnimatePresence>
            {courses.map((c) => (
              <AnimatedElement key={c.id}>
                <Link to={`/courses/${c.id}`} className="block w-full">
                  <Card title={c.title} className="courses">
                    <p className="text-sm text-muted-foreground">{c.description}</p>
                    <div className="mt-3 text-sm">
                      <span className="mr-4">Sections: {c.section_count}</span>
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
