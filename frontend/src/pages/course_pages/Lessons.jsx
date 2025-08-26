/* react */
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

/* pages */
import Home from "../Home.jsx";
import Courses from "./Courses.jsx";
import Sections from "./Sections.jsx";

/* components */
import Chat from "../../components/Chat.tsx";

/* api */
import { useApi } from "../../api/useApi.jsx";

/* Lessons */
export default function Lessons() {
   const { courseId, sectionId: sidString } = useParams();

   const parsed = Number.parseInt(sidString ?? "", 10);

   if (!Number.isInteger(parsed) || parsed <= 0) {
      return <div>Invalid section id: {sidString}</div>
   }
   
   const sectionId = parsed;
   const { listLessons } = useApi();
   const [lessons, setLessons] = useState([]);
   const [error,   setError  ] = useState(null);

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

   const [currentLesson, setCurrentLesson] = useState({});
   const [description,   setDescription  ] = useState("");
   const [showChat,      setShowChat     ] = useState(false);
   const [specialMess,   setSpecialMess] = useState("");

   function setSpecialMessage() {
     const lstatus = currentLesson["status"];
     console.log(currentLesson);
     if (lstatus === 0) {
       setSpecialMess("Start");
     }
     else if (lstatus === 1) {
       if (currentLesson.body_md === "") {
         setSpecialMess("Finish");
       }
       else {
         setSpecialMess("Continue");
       }
     }
     else {
       setSpecialMess("Finished");
     }
   }

  function showDescription(l) {
      if (!showChat) {
         setCurrentLesson(l);
         setDescription(l?.description ?? "");
      }
   }        

  const openLesson = () => {
    setSpecialMessage();
    setShowChat(true);
  }

   const initialMessages = useMemo(()=> {
        const raw = currentLesson.messages;
        if (Array.isArray(raw)) return raw;
        try {
          return raw ? JSON.parse(raw) : [];
        } catch {
          return [];
        }
      }, [currentLesson.id, currentLesson.messages]
   );

   if (error) return <div className="p-4 text-red-500">Error: {error}</div>;
   return (
      <div className="lessons">
         <h2 className="lessons-header">Lessons</h2>
         
         <div className="lessons-list">
            <ol className="dynamicList">
               {lessons.map((l) => (
                  <li key={l.id} onClick={() => showDescription(l)} style={l.id === currentLesson["id"] ? {border: "2px solid cyan"} : {border: "none"}}>{l.title}</li>
               ))}
            </ol>
         </div>

         <div className="lessons-interact">
            {showChat ? (
               <>
                  <Chat
                   purpose={"learn"}
                   sessionId={currentLesson.id}
                   disabled={!currentLesson.id}
                   height={260}
                   initialMessages={initialMessages}
                   specialBtn={true}
                   specialMess={specialMess}
                   />
                  <button onClick={() => setShowChat(false)}>Exit</button>
               </>
            ) : description ? (
               <>
                  <p>{description}</p>
                  <button onClick={() => openLesson()}>Open</button>
               </>
            ) : (
               <em>Select a lesson to see its description</em>
            )}
         </div>
      </div>
   );
}
