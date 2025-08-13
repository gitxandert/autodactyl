from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.router import RouterRunnable

from llm_operations.llm_class import LLM
from llm_operations.course_building.course_builder import build_course, approve_course

ROUTER_SYSTEM_PROMPT = """
You are a router that decides whether a user is:
    - asking for a new course
    - requesting a modification to a course
    - or approving a course

Return the string "build" if the user is initiating a course or requesting modifications to a course.

Return the string "approve" if the user expresses satisfaction with the total course design and doesn't request any changes.

*Return only either the string "build" or the string "approve".* 
**Do not return anything other than "build" or "approve".**
***If the user does not express disappoval or request changes, just return "approve".***
****You are not allowed to return anything other than "build" or "approve".****
*****If you return anything other than the string "build" or the string "approve", you will die.*****
"""

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    ("human", "{input}")
])

def route_course_message(message: str, session_id: str="buildcourse"):
    routes = {
            "build": RunnableLambda(lambda x: build_course(
                message=x["message"],
                session_id=x["session_id"],
                )),
            "approve": RunnableLambda(lambda x: approve_course(
                session_id=x["session_id"]
                ))
    }

    router = RouterRunnable(runnables=routes)
    llm = LLM.get_llm()

    router_chain = ROUTER_PROMPT | llm

    route_key = router_chain.invoke({"input": message})

    formatted_key = route_key.content.replace(" ", "")
    print(f"Route key = {formatted_key}")
    
    result = router.invoke({
        "key": formatted_key, 
        "input": {
            "message": message,
            "session_id": session_id
        }
    })

    return result
