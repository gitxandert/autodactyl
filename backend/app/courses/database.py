import sqlite3
import os

# status is 0, 1, or 2:
# - 0 = not started
# - 1 = started
# - 2 = finished
SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS courses (
  id          INTEGER PRIMARY KEY,
  slug        TEXT UNIQUE,
  title       TEXT NOT NULL,
  description TEXT NOT NULL,
  status      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sections (
  id        INTEGER PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  title     TEXT NOT NULL,
  summary   TEXT,
  position  INTEGER NOT NULL,
  status    INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE TABLE IF NOT EXISTS lessons (
  id            INTEGER PRIMARY KEY,
  course_id     INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id    INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  title         TEXT NOT NULL,
  description   TEXT NOT NULL,
  body_md       TEXT,
  messages      TEXT,
  summary       TEXT,
  position      INTEGER NOT NULL,
  status        INTEGER NOT NULL,
  UNIQUE(section_id, position)
);

CREATE TABLE IF NOT EXISTS exercises (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  prompt     TEXT NOT NULL,
  solution   TEXT,
  position   INTEGER NOT NULL,
  status     INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE TABLE IF NOT EXISTS quizzes (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  title      TEXT NOT NULL,
  position   INTEGER NOT NULL,
  status     INTEGER NOT NULL,
  UNIQUE(course_id, position)
);

CREATE TABLE IF NOT EXISTS projects (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
  brief      TEXT NOT NULL,
  position   INTEGER NOT NULL,
  status     INTEGER NOT NULL,
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
            "INSERT INTO courses(title, slug, description, status) VALUES (?, ?, ?, 0)",
            (title, slug, description),
    )

    print(f"Created {title}")
    return cur.lastrowid

def create_section(con, course_id, title, position):
    cur = con.execute(
            "INSERT INTO sections(course_id, title, position, status) VALUES (?, ?, ?, 0)",
            (course_id, title, position),
    )
    print(f"Added section {title}")
    return cur.lastrowid

def create_lesson(con, course_id, title, description, position, body_md = None, section_id=None):
    con.execute(
            "INSERT INTO lessons(course_id, section_id, title, description, body_md, position, status)"
            " VALUES (?, ?, ?, ?, ?, ?, 0)",
            (course_id, section_id, title, description, body_md, position),
    )
    print(f"Added lesson {title}")

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
        c.status                   AS status,

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

def get_sections(con: sqlite3.Connection, course_id: int):
    
    con.row_factory = sqlite3.Row

    sql = f"""
    SELECT
        s.id                       AS id,
        s.title                    AS title,
        s.status                   AS status,
        
        (SELECT COUNT(*)
         FROM lessons l
         WHERE l.section_id = s.id) AS lesson_count

    FROM sections AS s
    WHERE s.course_id = ?
    ORDER BY s.position;
    """
    rows = con.execute(sql, (course_id,)).fetchall()

    return [dict(r) for r in rows]

def get_lessons(con: sqlite3.Connection, section_id: int):
    
    con.row_factory = sqlite3.Row

    sql = f"""
    SELECT
        l.id                       AS id,
        l.title                    AS title,
        l.description              AS description,
        l.status                   AS status
    FROM lessons AS l
    WHERE l.section_id = ?
    ORDER BY l.position;
    """
    rows = con.execute(sql, (section_id,)).fetchall()

    return [dict(r) for r in rows]

def get_single_lesson(con: sqlite3.Connection, lesson_id: int):
    con.row_factory = sqlite3.Row

    sql = f"""
    SELECT
        l.course_id     AS course_id,
        l.section_id    AS section_id,
        l.title         AS title,
        l.description   AS description,
        l.body_md       AS body_md,
        l.messages      AS messages,
        l.summary       AS summary,
        l.status        AS status
    FROM lessons AS l
    WHERE l.id = ?
    """
    lesson = con.execute(sql, (lesson_id,)).fetchone()

    return lesson

def update_lesson_sql(con: sqlite3.Connection, l: dict):
        
    sql = f"""
    UPDATE lessons
    SET
        course_id   = ?,
        section_id  = ?,
        title       = ?,
        description = ?,
        body_md     = ?,
        messages    = ?,
        summary     = ?,
        status      = ?
    WHERE id = ?
    """
    con.execute(sql, (
        l["course_id"], l["section_id"], l["title"],
        l["description"], l["body_md"], l["messages"],
        l["summary"], l["status"]
        )
    )

    print(f"Updated lesson {l.title}")

def get_course_info(con: sqlite3.Connection, course_id: int):
    con.row_factory = sqlite3.Row

    sql = f"""
    SELECT
        c.title         AS title,
        c.description   AS description,
    FROM course AS c
    WHERE c.id = ?
    """
    course = con.execute(sql, (course_id,)).fetchone()

    return course["title"], course["description"]

def get_summaries(con: sqlite3.Connection, c_id: int, s_id: int, l_pos: int):
# if lesson's position = 1 and its section's position = 1,
# this is the start of the course
#
# if lesson's position = 1 and its section's position > 1,
# pull summaries from previous section(s)
#
# if lesson's position > 1 and its section's position = 1,
# pull summaries from previous lessons in the section
#
# if lesson's position > 1 and its section's position > 1,
# pull summaries from previous lessons in the section and previous sections
    con.row_factory = sqlite3.Row

    row = con.execute(
        """
        SELECT position AS sec_pos
        FROM sections
        WHERE id = ?
        """,
        (s_id,),
    ).fetchone()

    if row is None:
        return ""

    sec_pos = row["sec_pos"]

    if sec_pos == 1 and l_pos == 1:
        return ""

    rows = con.execute(
        """
        WITH cur AS (
            SELECT id AS section_id, course_id, position AS sec_pos
            FROM sections
            WHERE id = :sid
        ),
        prev_sections AS (
            SELECT s.id AS section_id, s.position AS sec_pos
            FROM sections s
            JOIN cur ON s.course_id = cur.course_id
            WHERE s.position < cur.sec_pos
        ),
        stream AS (
            
            SELECT
                s.position  AS sec_pos,
                0           AS kind_rank,
                NULL        AS lesson_pos,
                s.summary   AS text
            FROM sections s
            JOIN prev_sections ps ON ps.section_id = s.id
            
            UNION ALL

            SELECT
                cur.sec_pos AS sec_pos,
                1           AS kind_rank,
                l.position  AS lesson_pos,
                l.summary   AS text
            FROM lessons l
            JOIN cur ON l.section_id = cur.section_id
            WHERE l.position < :lpos
        )
        SELECT sec_pos, kind_rank, lesson_pos, text
        FROM stream
        ORDER BY sec_pos ASC, kind_rank ASC, lesson_pos ASC
        """,
        {"sid": s_id, "lpos": l_pos},
    ).fetchall()
    
    pieces = []
    for r in rows:
        txt: Optional[str] = r["text"]
        if txt is None:
            continue
        t = txt.strip()
        if t:
            pieces.append(t)

    return "\n\n".join(pieces)

def get_future_lessons(con: sqlite3.Connection, c_id: int, s_id: int, l_pos: int):
# pull all titles from lessons after l_pos to the end of the section
    pass
