from .models.llm import make_ollama_model
from .models.data import AllAnswers
import toml
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.run import AgentRunResult
from pydantic import BaseModel

class AnyAnswer(BaseModel):
    answer: str


class Extractor:

    def __init__(self, ):
        self.model = make_ollama_model()
        RESOURCES_DIR = Path(__file__).parent / "resources"
        with open(RESOURCES_DIR / "questions.toml") as f:
            questions = toml.load(f)
            self.prompt = questions["prompt"]

    def extract(self, text: str) -> AgentRunResult[AllAnswers]:
        agent = Agent(
            self.model,
            output_type=AllAnswers,
            instructions = self.prompt.format(text=text),
            retries=5,
        )
        try:
            result = agent.run_sync("")
        except Exception as e:
            print(f"Error in extract: {e}")
            return None
        return result
    
    def any_prompt(self, prompt: str):
        agent = Agent(
            self.model,
            output_type=AnyAnswer,
            instructions = prompt,
            retries=10,

        )
        try:
            result = agent.run_sync("")
        except Exception as e:
            print(f"Error in any_prompt: {e}")
            return None
        return result

    def __call__(self, text: str) -> AgentRunResult[AllAnswers]:
        return self.extract(text)

class GetQuestions():
    def __init__(self):
        pass
    
    def __call__(self, answers : AllAnswers) -> dict:
        return { answer.question_id: 
                    {'excerpt': answer.excerpt,
                     'answer': answer.answer} for answer in answers.answers }