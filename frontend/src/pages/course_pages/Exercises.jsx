export default function Exercises({ lid = null }) {
  return lid ? (
      <div>Hi I work</div>
    ) : ( 
      <div>Did you give me an id?</div>
    );
}

