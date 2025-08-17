import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Home from "../Home.jsx";
import Courses from "./Courses.jsx";
import Sections from "./Sections.jsx";
import { useApi } from "../../api/useApi.jsx";

export default function Lessons() {
   const { courseId, sectionId: sidString } = useParams();

   const parsed = Number.parseInt(sidString ?? "", 10);

   if (!Number.isInteger(parsed) || parsed <= 0) {
      return <div>Invalid section id: {sidString}</div>
   }
   
   const sectionId = parsed;
   {/* include interactiveLesson later */}
   const { LLMchat, listLessons } = useApi();
   const [lessons, setLessons] = useState([]);
   const [error, setError] = useState(null);

   useEffect(() => {
      (async () => {
         try {
            const data = await listLessons(sectionId);
            setLessons(data);
         } catch (e) {
            setError(e.message);
         }
      })();
   }, [listLessons]);

   const [currentLessonId, setCurrentLessonId] = useState(null);
   const [description, setDescription]         = useState("");
   const [showChat, setShowChat]               = useState(false);

   const showDescription = (id) =>  {
      const lesson = lessons.find(l => l.id === id);
      if (!showChat){
         setCurrentLessonId(lesson?.id ?? null);
         setDescription(lesson?.description ?? "");
      }
   }

   if (error) return <div className="p-4 text-red-500">Error: {error}</div>;
   return (
      <div className="lessons">
         <div className="lessons-nav">
            <Link to={`/sections/${courseId}`}><button>Sections</button></Link>
            <Link to="/courses"><button>Courses</button></Link>
            <Link to="/"><button>Home</button></Link>
         </div>

         <h2 className="lessons-header">Lessons</h2>

         <div className="lessons-list">
            <ol className="dynamicList">
               {lessons.map((l) => (
                  <li key={l.id} onClick={() => showDescription(l.id)} style={l.id === currentLessonId ? {border: "2px solid cyan"} : {border: "none"}}>{l.title}</li>
               ))}
            </ol>
         </div>

         <div className="lessons-interact">
            {showChat ? (
               <>
                  <p>showing chat</p>
                  <button onClick={() => setShowChat(false)}>Back</button>
               </>
            ) : description ? (
               <>
                  <p>{description}</p>
                  <button onClick={() => setShowChat(true)}>Start</button>
               </>
            ) : (
               <em>Select a lesson to see its description</em>
            )}
         </div>
      </div>
   );
}
