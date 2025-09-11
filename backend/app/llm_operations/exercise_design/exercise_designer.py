from typing import Any, Dict, List
import os
import psycopg

from langchain_core.prompts import PromptTemplate

import courses.database as db

from llm_operations.llm_class import LLM

EXERCISE_PROMPT = PromptTemplate.from_template("""
You are a teacher of a course called {course}. A student is asking you to give them an exercise based on information you have just taught in your lesson.

You will create an exercise for the student that is relevant to the course and can be solved with information provided in the lesson. If any information in this lesson builds on previous information, you may assume that the student already knows this information. For example, if the course is about algebra and the lesson is about polynomials, you may assume that the student already knows about variables. 

An exercise should not be able to be answered with merely "Yes" or "No". It should describe an action to accomplish or a problem to be solved. For example, an exercise may ask a student to write a function or solve a word problem.

Create an exercise for the following lesson:
{lesson}
""")

EXERCISE_SOLUTION_PROMPT = PromptTemplate.from_template("""
You are a teacher for a course called {course}.

You have just created an exercise for a lesson called {lesson} and need to have a solution for the exercise ready so that students can compare their solution with yours.

Return a solution to the following exercise:
{exercise}
""")

DB_PATH = os.environ["DATABASE_URL"]

class Exercise:
    _exercise = ""
    _solution = ""
    _cid = None
    _sid = None
    _lid = None
    
    @staticmethod
    def save_exercise():
        with psycopg.connect("DB_PATH") as con:
            if _cid is not None and _lid is not None:
                db.push_exercise_to_sql(con, Exercise._exercise, Exercise._solution, Exercise._cid, Exercise._sid, Exercise._lid);

    @staticmethod
    def hold_exercise(ex: str, sol: str, cid: int, sid: int, lid: int):
        _exercise = ex
        _solution = sol
        _cid = cid
        _sid = sid
        _lid = lid

    @staticmethod
    def reset():
        _exercise = ""
        _solution = ""
        _cid = None
        _sid = None
        _lid = None

def create_exercise(lid: int) -> Str:
    with psycopg.connect(DB_PATH) as con:
        lesson = db.get_single_lesson(con, lid)
        lesson = lesson["title"]
        cid = lesson["course_id"]
        sid = lesson["section_id"]
        course, _ = db.get_course_info(con, cid)
        messages = "\n\n".join(lesson["messages"])
    
    model = LLM.get_llm()

    chain = EXERCISE_PROMPT | model

    exercise = chain.invoke({
        "course":       course,
        "lesson_title": lesson,
        "lesson":       messages,
    }).content
    
    chain = EXERCISE_SOLUTION_PROMPT | model
    solution = chain.invoke({
        "course":   course,
        "lesson":   lesson,
        "exercise": exercise,
    }).content
    
    Exercise.hold_exercise(exercise, solution, cid, sid, lid);
    return exercise

def commit_exercise():
    Exercise.save_exercise();
    Exercise.reset();
