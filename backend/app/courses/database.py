import sqlite3
import os

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS courses (
  id          INTEGER PRIMARY KEY,
  slug        TEXT UNIQUE,
  title       TEXT NOT NULL,
  description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sections (
  id        INTEGER PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  title     TEXT NOT NULL,
  position  INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE TABLE IF NOT EXISTS lessons (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  title      TEXT NOT NULL,
  description TEXT NOT NULL,
  body_md    TEXT,
  position   INTEGER NOT NULL,
  UNIQUE(section_id, position)
);

CREATE TABLE IF NOT EXISTS exercises (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  prompt     TEXT NOT NULL,
  solution   TEXT,
  position   INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE TABLE IF NOT EXISTS quizzes (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  title      TEXT NOT NULL,
  position   INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE TABLE IF NOT EXISTS projects (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  brief      TEXT NOT NULL,
  position   INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE INDEX IF NOT EXISTS idx_lessons_course   ON lessons(course_id, position);
CREATE INDEX IF NOT EXISTS idx_exercises_course ON exercises(course_id, position);
CREATE INDEX IF NOT EXISTS idx_quizzes_course   ON quizzes(course_id, position);
CREATE INDEX IF NOT EXISTS idx_projects_course  ON projects(course_id, position);
CREATE INDEX IF NOT EXISTS idx_lessons_section   ON lessons(section_id);
CREATE INDEX IF NOT EXISTS idx_exercises_section ON exercises(section_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_section   ON quizzes(section_id);
CREATE INDEX IF NOT EXISTS idx_projects_section  ON projects(section_id);
"""

def init_db(path):
    """Create SQLite DB and schema if not present."""
    dirpath = os.path.dirname(path)
    if dirpath:  
        os.makedirs(dirpath, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        # Ensure FK enforcement for *this* connection
        conn.execute("PRAGMA foreign_keys = ON;")
        # Create all tables/indexes
        conn.executescript(SCHEMA)

def open_db(path):
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def create_course(con, title, slug=None, description=None):
    cur = con.execute(
            "INSERT INTO courses(title, slug, description) VALUES (?, ?, ?)",
            (title, slug, description),
    )

    print(f"Created {title}")
    return cur.lastrowid

def add_lesson(con, course_id, title, description, position, body_md = None, section_id=None):
    con.execute(
            "INSERT INTO lessons(course_id, section_id, title, description, body_md, position)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (course_id, section_id, title, description, body_md, position),
    )
    print(f"Added lesson {title}")

def create_section(con, course_id, title, position):
    cur = con.execute(
            "INSERT INTO sections(course_id, title, position) VALUES (?, ?, ?)",
            (course_id, title, position),
    )
    print(f"Added section {title}")
    return cur.lastrowid

def print_course(con, course_id: int):
    print("\n=== COURSE ===")
    row = con.execute(
        "SELECT id, title, slug, description FROM courses WHERE id = ?",
        (course_id,),
    ).fetchone()
    if not row:
        print(f"No course found with id={course_id}")
        return
    cid, title, slug, desc = row
    print(f"ID: {cid}\nTitle: {title}\nSlug: {slug}\nDescription: {desc or ''}")

    print("\n--- SECTIONS ---")
    sections = con.execute(
        "SELECT id, title, position FROM sections WHERE course_id = ? ORDER BY position",
        (cid,),
    ).fetchall()
    if not sections:
        print("(none)")
    for sid, stitle, spos in sections:
        print(f"[{sid}] {stitle} (pos {spos})")

    print("\n--- LESSONS ---")
    lessons = con.execute(
        """SELECT id, title, position, section_id
           FROM lessons
           WHERE course_id = ?
           ORDER BY position""",
        (cid,),
    ).fetchall()
    for lid, ltitle, lpos, sec_id in lessons:
        print(f"[{lid}] {ltitle} (pos {lpos}, section {sec_id})")

def get_all_courses(con: sqlite3.Connection): 
    # eventually take a user_id argument

    con.row_factory = sqlite3.Row
    
    # where = "WHERE c.user_id = ?" if user_id is not None else ""
    # params = [user_id] if user_id is not None else []

    sql = f"""
    SELECT
        c.id                       AS id,
        c.title                    AS title,
        c.description              AS description,
        
        (SELECT COUNT(*)
         FROM sections s
         WHERE s.course_id = c.id) AS section_count,

        (SELECT COUNT(*)
         FROM lessons l
         WHERE l.course_id = c.id) AS lesson_count

    FROM courses AS c
    ORDER BY c.id DESC;
    """
    rows = con.execute(sql).fetchall()

    return [dict(r) for r in rows]
