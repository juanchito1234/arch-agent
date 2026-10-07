from groq import Groq

from config.settings import (
    GROQ_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
)

from agent.prompt import SYSTEM_PROMPT


class ArchitectureAgent:

    def __init__(
        self,
        api_key: str = GROQ_API_KEY,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def build_messages(self, history: list, user_input: str) -> list:
        messages = []

        if SYSTEM_PROMPT.strip():
            messages.append({
                "role": "system",
                "content": SYSTEM_PROMPT.strip()
            })

        messages.extend(history)

        messages.append({
            "role": "user",
            "content": user_input
        })

        return messages

    def generate_response(self, history: list, user_input: str):
        messages = self.build_messages(history, user_input)

        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )