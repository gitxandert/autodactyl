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

// this will need to take a user_id eventually
   const listCourses = async () => {
      const res = await fetch(`${base}/api/list-courses`, {
         method: "GET",
         credentials: "include",
         headers: { "Accept": "application.json" },
      });
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      /** @type {CourseSummary[]} */
      const json = await res.json();
      return json;
  };

   return {
      buildCourse,
      approveCourse,
      listCourses
  };
}

