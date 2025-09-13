from langchain_core.prompts import PromptTemplate

from llm_operations.llm_class import LLM

import os
import psycopg

import courses.database as db
DB_PATH = os.environ["DATABASE_URL"]

LESSON_PROMPT = PromptTemplate.from_template("""
You are writing a lesson script.

Write a comprehensive lesson script based on the lesson's title and description. Keep it pertinent to the course as described in 'Course title' and 'Course description'. You may build upon previously-learned content if summaries of previous lessons and/or sections are provided and/or lay the groundwork for future lessons if future lessons are provided.

Parse the lesson you generate into multiple paragraphs. **DO NOT LABLE YOUR PARAGRAPHS.** Each paragraph should focus on one or multiple pivotal concepts. Limit paragraphs to between 3 and 5 sentences; if a single concept requires more sentences than this, break up your teaching of it into multiple paragraphs. If concepts can be described in fewer than three sentences, then you may describe multiple concepts in a single paragraph (if they are related). At the end of each paragraph, always ask the student if they would like clarification or elaboration of any of the content presented so far. **DO NOT PRESUME THE STUDENT'S QUESTION.**

Course title: {c_title}
Course description: {c_description}
Lesson title: {l_title}
Lesson description: {l_description}
Previous lesson/section summaries: {summaries}
Future lessons: {future_lessons}
""")

def generate_lesson(l: dict):
    con = db.open_db()
    c_title, c_description = db.get_course_info(con, l["course_id"])
    summaries = db.get_summaries(con, 
                                  l["course_id"],
                                  l["section_id"], 
                                  l["position"])
    future_lessons = db.get_future_lessons(con, 
                                            l["course_id"],
                                            l["section_id"], 
                                            l["position"])

    description = l["description"]
    title = l["title"]
    llm = LLM.get_llm()
    chain = LESSON_PROMPT | llm
    result = chain.invoke({
        "c_description": c_description,
        "c_title": c_title,
        "future_lessons": future_lessons,
        "l_description": description,
        "l_title": title,
        "summaries": summaries
    })

    return result.content

ANSWER_PROMPT = PromptTemplate.from_template("""
You are a teacher named Assistant answering a question by a student named User.
Reply to exactly what User asks, being informative, thorough, and kind.
Consider User's question from the context of your conversation: 

{context}

Student's question: {question}
""")

def answer_lesson_question(question: str, prev_messages: str):
    llm = LLM.get_llm()
    chain = ANSWER_PROMPT | llm
    result = chain.invoke({
        "question": question,
        "context": prev_messages
    })

    return result.content

SUMMARY_PROMPT = PromptTemplate.from_template("""
You are summarizing a lesson that you have just delivered, as well as the discussion that you and your student had about it. Don't just repeat what was said, but provide a concise summary of it. Constrain the length of the summary to one paragraph.

Lesson and discussion:
{messages}
""")

def summarize_lesson(messages: str):
    llm = LLM.get_llm()
    chain = SUMMARY_PROMPT | llm
    result = chain.invoke({
        "messages": messages,
    })

    return result.content

def format_as_ChatMsg(mid: int, role: str, content: str):
    return {"id": mid,
            "role": role,
            "content": content}
