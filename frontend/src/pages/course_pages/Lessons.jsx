/* react */
import { useEffect, useState } from "react";
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
   const { listLessons, LLMChat } = useApi();
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

   const [currentLesson, setCurrentLesson] = useState(null);
   const [description,   setDescription  ] = useState("");
   const [showChat,      setShowChat     ] = useState(false);

   const showDescription = (id) =>  {
      if (!showChat) {
         const lesson = lessons.find(l => l.id === id);
         setCurrentLesson(lesson);
         setDescription(lesson?.description ?? "");
      }
   }
   
   const [btnFunction, setBtnFunction]  = useState("")
   const [btnDisabled, setBtnDisabled]  = useState(false);
   const [busy,        setBusy       ]  = useState(false);
   
   const setChatButton = () => {
      if (!showChat) {
         if (currentLesson.status == 0) {
            setBtnFunction("Start");
         }
         else {
            setBtnFunction("Return");
         }
      }
      else {
         if (currentLesson.status == 1) {
            if (currentLesson.body_md != "") {
               setBtnFunction("Continue");
            }
            else {
               setBtnFunction("Finish");
            }
         }
         else {
            setBtnFunction("Completed");
            setBtnDisabled(true);
         }
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
                  <li key={l.id} onClick={() => showDescription(l.id)} style={l.id === currentLesson["id"] ? {border: "2px solid cyan"} : {border: "none"}}>{l.title}</li>
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
                   initialMessages=currentLesson.messages
                   footerExtras={(
                      <button onClick={sendBtnMess} disabled={btnDisabled || busy}>
                        {btnFunction}
                      </button>
                   )}
                   />
                  <button onClick={() => setShowChat(false)}>Back</button>
               </>
            ) : description ? (
               <>
                  <script>setChatButton</script>
                  <p>{description}</p>
                  <button onClick={sendBtnMess}>{btnFunction}</button>
               </>
            ) : (
               <em>Select a lesson to see its description</em>
            )}
         </div>
      </div>
   );
}
