import { useEffect, useState } from "react";

import { useApi } from "../../api/useApi.jsx";
import Exercise   from "../../components/Exercise.jsx";

export default function Exercises({ lid = null }) {
  const { listExercises, getExercise, newExercise } = useApi();
  const [exercises, setExercises]    = useState([]);
  const [adHocEx,   setAdHocEx  ]    = useState({});
  const [error,     setError    ]    = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await listExercises(lid);
        if (data) {
          setExercises(data);
        }
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [listExercises]);

  if (error) return <div>Error: {error}</div>

  async function createExercise() {
    try {
      const data = await newExercise(lid);
      
      setAdHocEx(data);
    }
  }

  return (
    <div className="exercises-container">
      <div>
        {exercises.map((e) => (
          <Exercise key={e.id} title={e.title} />
        ))}
      </div>
      <button onClick={() => createExercise()}>+ New Exercise</button>
    </div>
  );
}

