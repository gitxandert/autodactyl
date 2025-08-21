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

import sqlite3

from courses.database import get_single_lesson, update_lesson_sql
from llm_operations.course_teaching.lesson_generator import generate_lesson, generate_summary
from llm_operations.course_teaching.lesson_helpers import iterate_body_md, answer_lesson_question 

class LessonSessions:
    _sessions = {}

    @staticmethod
    def get_lesson(lesson_id: int):
        lesson = LessonSessions._sessions.get(lesson_id)
        if lesson is not None:
            return lesson
        else:
            with sqlite3.connect(DB_PATH) as con:
                LessonSessions._sessions[lesson_id] = get_single_lesson(lesson_id)
            return LessonSessions._sessions[lesson_id]

    @staticmethod
    def update_lesson(lesson_id: int, lesson):
        LessonSessions._sessions[lesson_id] = lesson

    @staticmethod
    def push_to_sql(lesson):
        with sqlite3.connect(DB_PATH) as con:
            update_lesson_sql(con, lesson)
        LessonSessions._sessions = {}

# need to check if LLMChat expects all of the messages or just new ones;
# probably should 
def iterate_lesson(message: str, session_id: str):
    # convert session_id to int for SQL
    lid = int(session_id)
    
    # get lesson from LessonSessions (pulls lesson from SQL if not stored)
    lesson = LessonSessions.get_lesson(lid)

    return_message = ""
    
    if message == "Return" or lesson["status"] == 2:
        # the user is returning to a lesson, or the lesson has finished
        # (status set to 2 if lesson is finished); return all messages
        return lesson["messages"]
    elif message == "Leave":
        # the user is leaving the session
        if lesson["status"] == 1:
            # if the lesson has started, but not finished
            LessonSessions.push_to_SQL(lesson)
        return "Goodbye!"       
    elif message == "Finish":
        # the user has clicked "Finish"
        lesson["status"] = 2 # status 2 means lesson is finished
        summary = generate_summary(lesson["messages"])
        lesson["summary"] = summary
        lesson["messages"].append(summary)
        LessonSession.push_to_SQL(lesson)
        return summary
    elif message == "Start" or lesson["status"] == 0:
        # the user is starting a lesson for the first time
        # (status set to 0 if lesson has not been started)
        lesson["body_md"] = generate_lesson(lesson)
        lesson["status"] = 1 # status 1 means lesson has started
        lesson["body_md"], return_message = iterate_body_md(lesson["body_md"])
        lesson["messages"].append(return_message)
    elif message == "Continue":
        # the user is continuing a lesson, so the next part of body_md
        # needs to be added to lesson["messages"]
        lesson["body_md"], return_message = iterate_body_md(lesson["body_md"])
        lesson["messages"].append(return_message)
    else:
        # if none of the former options are the case, then the user has
        # asked a question; answer_lesson_question will append the user's
        # message and the assistant's response to lesson["messages"]
        return_message = answer_lesson_question(message, lesson["messages"])
        lesson["messages"].append(message)
        lesson["messages"].append(return_message)
    
    # update the lesson
    LessonSessions.update_lesson(lid, lesson)

    return return_message
