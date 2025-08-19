from langchain_core.prompts import PromptTemplate

from llm_operations.llm_class import LLM

import sqlite3
from courses.database import get_course_info, get_summaries, get_future_lessons


LESSON_GENERATE_PROMPT = PromptTemplate.from_template("""
You are generating a lesson for a course. You rely on the course's title and description and the lesson's title and description, as well as (if provided) previous lesson/section summaries and/or titles of future lessons.

Generate a comprehensive lesson based on the lesson's title and description. Keep it pertinent to the course (as described in the course's title and description). You may build upon previously-learned content (if summaries of previous lessons and/or sections are provided) and/or lay the groundwork for future lessons (if future lesson titles are provided).

Parse the lesson you generate into paragraphs that teach about one or multiple pivotal concepts. Limit paragraphs to between 3 and 5 sentences; if a single concept requires more sentences than this, break up your teaching of it into multiple paragraphs. If concepts can be described in fewer than three sentences, than you may describe multiple concepts in a single paragraph (if they are related).

At the end of each paragraph, always ask the user if they would like clarification or elaboration of any of the content presented so far.

Course title: {c_title}
Course description: {c_description}
Lesson title: {l_title}
Lesson description: {l_description}
Previous lesson/section summaries: {summaries}
Future lesson titles: {future_lessons}
""")

def generate_lesson(l: dict):
    with sqlite3.connect(DB_PATH) as con:
        c_title, c_description = get_course_info(con, l["course_id"])
        summaries = get_summaries(con, 
                                  l["course_id"],
                                  l["section_id"], 
                                  l["position"])
        future_lesson_titles = get_future_lessons(con,
                                                  l["course_id"],
                                                  l["section_id"], 
                                                  l["position"])

    llm = LLM.get_llm()
    chain = LESSON_GENERATE_PROMPT | llm
    result = chain.invoke({
        "c_title": c_title,
        "c_description": c_description,
        "l_title": l["title"],
        "l_descripton": l["description"],
        "future_lessons": future_lesson_titles,
        "summaries": summaries
    })

    return result.content
