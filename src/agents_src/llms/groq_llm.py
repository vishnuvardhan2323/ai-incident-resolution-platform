from crewai import LLM

from src.rag_src.config.rag_settings import rag_settings


class GroqCompatibleLLM(LLM):

    def call(self, messages, *args, **kwargs):

        # CrewAI may add cache_breakpoint.
        # Groq does not support it.
        if isinstance(messages, list):
            for message in messages:
                if isinstance(message, dict):
                    message.pop("cache_breakpoint", None)

        return super().call(messages, *args, **kwargs)


groq_llm = GroqCompatibleLLM(
    model=f"groq/{rag_settings.GROQ_MODEL}",
    api_key=rag_settings.GROQ_API_KEY,
    temperature=0.1
)