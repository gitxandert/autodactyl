export default function Draft({ draft = {}, height = 400 }) {
  return (
    <div className="draft space-y-0" style={{ height }}> 
      <div className="draft-course">
        <h2 style={{ margin: 0 }}>{draft.title}</h2>
        <div>{draft.description}</div>
      </div>
      {draft.sections.map((s) => (
        <div>
          <h3 className="draft-section" style={{ margin: 0 }}>{s.title}</h3>
          {s.lessons.map((l) => (
            <div className="draft-lesson">
              <h4 style={{ margin: 0 }}>{l.title}</h4>
              <div>{l.description}</div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
