import { useEffect, useState } from "react";

import { useApi } from "../../api/useApi.jsx";
import Exercise   from "../../components/Exercise.jsx";

export default function Exercises({ lid = null }) {
  const     { listExercises }     = useApi();
  const [exercises, setExercises] = useState([]);
  const [error,     setError    ] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await listExercises(lid);
        setExercises(data);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [listExercises]);

  if (error) return <div>Error: {error}</div>

  return lid ? (
    {exercises.map((e) => (
      <Exercise key={e.id} title={e.title} />
    }
      <div>`Showing lesson ${lid}'s exercises`</div>
    ) : ( 
      <div>Did you give me an id?</div>
    );
}

