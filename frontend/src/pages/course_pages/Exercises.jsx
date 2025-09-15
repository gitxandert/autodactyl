export default function Exercises({ lid = null }) {
  return lid ? (
      <div>`Showing lesson ${lid}'s lessons`</div>
    ) : ( 
      <div>Did you give me an id?</div>
    );
}

