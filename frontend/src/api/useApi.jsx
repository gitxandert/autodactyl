import { useCallback } from "react";

const API_BASE = (import.meta?.env?.VITE_API_BASE ?? "").replace(/\/$/, ""); 

export function useApi(base = API_BASE) {
   const getUser = useCallback(async () => {
      const res = await fetch(`${base}/api/me`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      console.log(res);
      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to get user info.");
      
      return json.result;
   }, []);

   const LLMchat = async ({purpose, message, session_id}) => {
      console.log(purpose, message, session_id);
      const sid = String(session_id);
      const res = await fetch(`${base}/api/chat`, {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ 
            purpose, 
            message, 
            session_id: sid
         }),
      });
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      return res.json();
   };

   const approveCourse = async (session_id) => {
      const res = await fetch(`${base}/api/approve`, {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ session_id }),
         });
         if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
         return res.json();
   };

   const listCourses = useCallback(async () => {
      const res = await fetch(`${base}/api/list-courses`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);

      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to list courses.");

      return json.result;
   }, []);

   const listSections = useCallback(async (course_id) => {
      const id = Number(course_id);
      const res = await fetch(`${base}/api/list-sections?course_id=${id}`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);

      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to list sections.");

      return json.result;
   },[]);

   const listLessons = useCallback(async (section_id) => {
      const id = Number(section_id);
      const res = await fetch(`${base}/api/list-lessons?section_id=${id}`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);

      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to list lessons.");

      return json.result;
   },[]);

  const listExercises = useCallback(async (lesson_id) => {
      const id = Number(lesson_id);
      const res = await fetch(`${base}/api/list-exercises?lesson_id=${id}`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);

      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to list exercises.");

      return json.result;
   },[]);

  const getExercise = useCallback(async (ex_id) => {
      const id = Number(ex_id);
      const res = await fetch(`${base}/api/get-exercise?ex_id=${id}`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);

      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to get exercise.");

      return json.result;
   },[]);

  const newExercise = useCallback(async (l_id) => {
      const id = Number(l_id);
      const res = await fetch(`${base}/api/new-exercise?l_id=${id}`, {
         credentials: "include",
         headers: { Accept: "application/json" },
      });

      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);

      const json = await res.json();
      if (!json.ok) throw new Error(json.error || "Failed to create exercise.");

      return json.result;
   },[]);
  
   return {
      getUser,
      LLMchat,
      approveCourse,
      listCourses,
      listSections,
      listLessons,
      listExercises,
      getExercise
   };
}

