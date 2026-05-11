import os

from dotenv import load_dotenv
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.providers.ollama import OllamaProvider


def make_azure_model() -> Model:
    load_dotenv()
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    #print(api_key, endpoint, api_version, deployment_name)
    return OpenAIChatModel(
        model_name=deployment_name,
        provider=AzureProvider(
            azure_endpoint=endpoint,
            api_version=api_version,
            api_key=api_key,
        ),
        settings=OpenAIChatModelSettings(
            temperature=0.1,
        )
    )

def make_ollama_model(model_name = 'gpt-oss:20b') -> Model:
    model = OpenAIChatModel(
        model_name=model_name,
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
    )
    return model

