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

EXERCISE_TITLE_PROMPT = PromptTemplate.from_template("""
You have just created an exercise for a course called {course}.

Create a short title (between two and five words) for the exercise.
*Do not reveal the solution to the exercise in the title.*

Here is the exercise:
{exercise}
""")

DB_PATH = os.environ["DATABASE_URL"]

class Exercise:
    _exercise = ""
    _title    = ""
    _solution = ""
    _lid = None
    
    @staticmethod
    def save_exercise():
        with psycopg.connect("DB_PATH") as con:
            if Exercise._lid is not None:
                db.push_exercise_to_sql(con, Exercise._lid, Exercise._title, Exercise._exercise, Exercise._solution);

    @staticmethod
    def hold_exercise(ex: str, sol: str, tit: str, lid: int):
        Exercise._exercise = ex
        Exercise._title    = tit
        Exercise._solution = sol
        Exercise._lid      = lid

    @staticmethod
    def reset():
        Exercise._exercise = ""
        Exercise._tit      = ""
        Exercise._solution = ""
        Exercise._lid      = None

def create_exercise(lid: int) -> Str:
    with psycopg.connect(DB_PATH) as con:
        lesson = db.get_single_lesson(con, lid)
        lesson = lesson["title"]
        cid = lesson["course_id"]
        course, _ = db.get_course_info(con, cid)
        messages = "\n\n".join(lesson["messages"])
    
    model = LLM.get_llm()

    chain = EXERCISE_PROMPT | model

    exercise = chain.invoke({
        "course":       course,
        "lesson_title": lesson,
        "lesson":       messages,
    }).content
    
    chain = EXERCISE_TITLE_PROMPT | model
    title = chain.invoke({
        "course":   course,
        "exercise": exercise,
    }).content

    chain = EXERCISE_SOLUTION_PROMPT | model
    solution = chain.invoke({
        "course":   course,
        "lesson":   lesson,
        "exercise": exercise,
    }).content
    
    Exercise.hold_exercise(exercise, title, solution, lid);
    return exercise

def commit_exercise():
    Exercise.save_exercise();
    Exercise.reset();
