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

DB_PATH = os.environ["DATABASE_URL"]

class Exercise:
    _exercise = ""
    _answer = ""
    _explanation = ""
    _cid = None
    _sid = None
    _lid = None
    
    @staticmethod
    def save_exercise():
        with psycopg.connect("DB_PATH") as con:
            if _cid is not None and _lid is not None:
                db.push_exercise_to_sql(con, Exercise._exercise, Exercise._answer, Exercise._cid, Exercise.sid, Exercise._lid);

    @staticmethod
    def hold_exercise(ex: str):
        _exercise = ex
        _cid = cid
        _sid = sid
        _lid = lid
  
    @staticmethod
    def hold_answer(an: str):
        _answer = an

    @staticmethod
    def get_exercise() -> Str:
        return Exercise._exercise

    @staticmethod
    def get_answer() -> Str:
        return Exercise._answer

    @staticmethod
    def get_explanation() -> Str:
        return Exercise._explanation

    @staticmethod
    def reset():
        _exercise = ""
        _answer = ""
        _cid = None
        _sid = None
        _lid = None

def create_exercise(lid: int) -> Str:
    with psycopg.connect(DB_PATH) as con:
        lesson = db.get_single_lesson(con, lid)
        cid = lesson["course_id"]
        sid = lesson["section_id"]
        course, _ = db.get_course_info(con, cid)
        messages = "\n\n".join(lesson["messages"])
    
    model = LLM.get_llm()

    chain = EXERCISE_PROMPT | model

    exercise = chain.invoke({
        "courses": course,
        "lesson": messages,
    }).content

    Exercise.hold_exercise(exercise, cid, sid, lid);
    return exercise

ANSWER_EXERCISE_PROMPT = PromptTemplate.from_template("""
You are a teacher for a course called {course}.

""")

def create_answer(model):
    exercise = Exercise.get_exercise()
    model = LLM.get_llm()
    chain = ANSWER_EXERCISE_PROMPT | model
    answer = chain.invoke({
        "exercise": exercise,
    }).content
    
    Exercise.hold_answer(answer)
    return answer

def commit_exercise():
    Exercise.save_exercise();
    Exercise.reset();
