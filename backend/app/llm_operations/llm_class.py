from langchain_ollama import ChatOllama
import os

class LLM:
    __llm = None

    @staticmethod
    def get_llm():
        if LLM.__llm == None:
            LLM.__llm = ChatOllama(
                model='qwen2:7b-instruct',
                base_url=os.getenv("MODEL_URL", "http://ollama:11434"),
                temperature=0
            )
        return LLM.__llm
