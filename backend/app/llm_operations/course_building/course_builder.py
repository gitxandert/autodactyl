from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from llm_operations.llm_class import LLM

import json, sqlite3
from textwrap import dedent

from llm_operations.course_building.build_utilities import _slugify, _validate_draft
from courses.database import open_db, create_course, add_lesson, create_section, print_course

class CourseBuildSession:
    _session = {}
    _draft = {}

    @staticmethod
    def get_history(session_id: str):
        return CourseBuildSession._session.setdefault(session_id, InMemoryChatMessageHistory())
    
    @staticmethod
    def set_draft(draft: dict):
        CourseBuildSession._draft = draft
        print(f"{draft}")

    @staticmethod
    def get_draft():
        return CourseBuildSession._draft

    @staticmethod
    def reset_draft():
        CourseBuildSession._draft = {}

def set_draft(draft: dict):
    CourseBuildSession.set_draft(draft)

def get_draft():
    return CourseBuildSession.get_draft()

def reset_draft():
    CourseBuildSession.reset_draft()

class JsonOutputParser(BaseOutputParser):
    def parse(self, text: str):
        return json.loads(text)

SYSTEM_PROMPT = dedent("""
You are helping someone design a course. Courses are structured as sections broken up into lessons.

Your job is to respond ONLY with valid JSON that matches this format exactly:

{{
  "response": "A short, friendly explanation of the course structure and a question asking the user if they would like any changes.",
  "draft": {{
    "title": "Course Title",
    "description": "Short Course Description",
    "sections": [
      {{
        "title": "Section 1 Title",
        "lessons": [
          {{"title": "Lesson 1 Title", "description": "Short lesson description"}},
          {{"title": "Lesson 2 Title", "description": "Short lesson description"}}
        ]
      }}
    ]
  }}
}}

Rules:
- Never include text outside of the JSON object.
- Always include the full updated course design in "draft", even when making small changes.
- Only change the course if the user specifically requests it.
- Do not include information about videos, forums, or any external educational resources.
- The "response" field must always end with a question asking for user approval.
""")

COURSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("placeholder", "{history}"),
    ("human", "{input}")
])

def build_course(message: str, session_id: str="buildcourse"):
    model = LLM.get_llm().bind(
            format="json", 
            options={
                "temperature": 0.2, 
                "num_ctx": 8192
            }
        )

    print(f"{session_id}")

    chain = COURSE_PROMPT | model | JsonOutputParser()

    chain_with_memory = RunnableWithMessageHistory(
            chain, CourseBuildSession.get_history,
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="response"
    )

    cfg = {"configurable": {"session_id": session_id}}

    return chain_with_memory.invoke({"input": message}, cfg)

def approve_course(session_id: str, db_path: str) -> int:
    """
    Pull the last AI draft for `session_id`, parse/validate it, and write to SQLite.
    Returns the new course_id.
    """
    # 1) get the approved draft
    draft = get_draft()

    # 2) validate & normalize
    title, description, sections = _validate_draft(draft)
    slug = _slugify(title)

    # 3) upsert-ish slug guard (optional): ensure unique slugs by suffixing -2, -3, ...
    def _ensure_unique_slug(con, base_slug: str) -> str:
        s = base_slug
        n = 1
        while True:
            row = con.execute("SELECT 1 FROM courses WHERE slug = ? LIMIT 1", (s,)).fetchone()
            if not row:
                return s
            n += 1
            s = f"{base_slug}-{n}"

    # 4) write to DB: transactionally
    con = open_db(db_path)
    try:
        with con:
            unique_slug = _ensure_unique_slug(con, slug)
            course_id = create_course(
                con, title=title, slug=unique_slug, description=description
            )

            # iterate the *normalized* sections
            for sec in sections:
                section_id = create_section(
                    con,
                    course_id=course_id,
                    title=sec["title"].strip(),
                    position=int(sec["position"]),
                )

                # nest lessons under their section
                for l in sec["lessons"]:
                    add_lesson(
                        con,
                        course_id=course_id,
                        title=l["title"].strip(),
                        description=l["description"],
                        position=int(l["position"]),
                        section_id=section_id,
                    )

        reset_draft()
        print_course(con, course_id)
        return course_id
    finally:
        con.close() 
