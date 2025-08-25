# - convert session_id (actually lesson_id) to int 'id'
# - use id to pull the lesson
# - if lesson's messages are empty:
#   - call lesson-generator to generate a lesson
#       - lesson-generator reads course and lesson description
#       - if previous lessons have been generated, lesson-generator also reads
#         the lesson's section's summaries to see what has already been covered
#   - assistant figures out where pauses for questions and/or depth should be
# - if lesson has stored messages:
#   - lesson's messages field is parsed into assistant and learner messages
#       - as parts of a lesson enter the conversation, they are removed from
#         from body_md
# - if body_md has content, continue iterating through content at the learner's 
#   bequest
# - if body_md does not have content, simply display messages, with no option
#   to continue

import os, sqlite3, json

from courses.database import get_single_lesson, update_lesson_sql
from llm_operations.course_teaching.lesson_helpers import generate_lesson, answer_lesson_question, summarize_lesson, format_as_ChatMsg

DB_PATH = os.environ.get("SQLITE_PATH", "app/courses/database/courses.sqlite")

class LessonSession:
    _session = {}

    @staticmethod
    def get_lesson(lesson_id: int):
        lesson = LessonSession._session.get(lesson_id)
        if lesson is not None:
            return lesson
        else:
            with sqlite3.connect(DB_PATH) as con:
                LessonSession._session[lesson_id] = get_single_lesson(con, lesson_id)
            return LessonSession._session[lesson_id]

    @staticmethod
    def update_lesson(lesson_id: int, lesson):
        LessonSession._session[lesson_id] = lesson
        LessonSession.push_to_sql(lesson)

    @staticmethod
    def push_to_sql(lesson):
        with sqlite3.connect(DB_PATH) as con:
            update_lesson_sql(con, lesson)
        LessonSession._session = {}

def iterate_body_md(body_md: str):
    print(f"{body_md}")
    parts = body_md.split("\n\n", 1)
    first_paragraph = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    return first_paragraph, rest

def add_message(lesson, lid, new_message, role):
    raw = lesson["messages"]
    try:
        messages = json.loads(raw)
    except Exception:
        messages = []

    messages.append(format_as_ChatMsg(lid, role, new_message));
    lesson["messages"] = json.dumps(messages)
 
def iterate_lesson(message: str, session_id: str):
    # convert session_id to int for SQL
    lid = int(session_id)

    # get lesson from LessonSessions (pulls lesson from SQL if not stored)
    lesson = LessonSession.get_lesson(lid)

    return_message = ""
    
    if message == "Leave":
        # the user is leaving the session
        if lesson["status"] == 1:
            # if the lesson has started, but not finished
            LessonSession.push_to_SQL(lesson)
        return "Goodbye!"       
    elif message == "Finish":
        # the user has clicked "Finish"
        summary = summarize_lesson(lesson["messages"])
        lesson["summary"] = summary
        add_message(lesson, lid, summary, "application") 
        lesson["status"] = 2
        LessonSession.push_to_sql(lesson)
        return {"response": summary}
    elif message == "Start":
        # the user is starting a lesson for the first time
        # (status set to 0 if lesson has not been started)
        print("generating lesson")
        lesson["body_md"] = generate_lesson(lesson)
        lesson["status"] = 1 # status 1 means lesson has started
        return_message, lesson["body_md"] = iterate_body_md(lesson["body_md"])
    elif message == "Resume" or  message == "Continue":
        # the user is continuing a lesson, so the next part of body_md
        # needs to be added to lesson["messages"]
        return_message, lesson["body_md"] = iterate_body_md(lesson["body_md"])
    else:
        # if none of the former options are the case, then the user has
        # asked a question; answer_lesson_question will append the user's
        # message and the assistant's response to lesson["messages"]
        messages = json.loads(lesson["messages"])
        return_message = answer_lesson_question(message, ".\n\n".join([m["content"] for m in messages]))
        add_message(lesson, lid, message, "user") 
    # update the lesson
    add_message(lesson, lid, return_message, "application") 
    LessonSession.update_lesson(lid, lesson)
    
    response = {"response": return_message, "status": lesson["status"], "body_md": lesson["body_md"]}
    return response
