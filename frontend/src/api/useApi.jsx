import { useCallback } from "react";

const API_BASE = (import.meta?.env?.VITE_API_BASE ?? "").replace(/\/$/, ""); 

export function useApi(base = API_BASE) {
   const buildCourse = async (message, session_id) => {
      const res = await fetch(`${base}/api/build-course`, {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ message, session_id }),
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

// this will need to incorporate a user_id eventually
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

   return {
      buildCourse,
      approveCourse,
      listCourses,
      listSections
   };
}

