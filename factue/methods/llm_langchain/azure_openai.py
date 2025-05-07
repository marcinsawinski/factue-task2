import os

from dotenv import load_dotenv
from langchain_openai import (AzureChatOpenAI, AzureOpenAI,
                              AzureOpenAIEmbeddings)
from pydantic import SecretStr

from factue.utils.types import ModelMode

load_dotenv()
azure_openai_api_key = SecretStr(os.getenv("AZURE_OPENAI_API_KEY", ""))
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")
azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")


def init_azure_openai(
    streaming=False,
    mode=ModelMode.CHAT,
    temperature=0.0,
    max_retries=2,
    seed=0,
    resource_id=None,  # TODO alterative endpoints ?
):

    if mode == ModelMode.CHAT:
        return AzureChatOpenAI(
            azure_deployment=azure_openai_deployment,
            api_version=azure_openai_api_version,
            api_key=azure_openai_api_key,
            temperature=temperature,
            streaming=streaming,
            max_retries=max_retries,
            seed=seed,
        )
    elif mode == ModelMode.LLM:
        return AzureOpenAI(
            azure_deployment=azure_openai_deployment,
            api_version=azure_openai_api_version,
            api_key=azure_openai_api_key,
            temperature=temperature,
            streaming=streaming,
            max_retries=max_retries,
            seed=seed,
        )
    elif mode == ModelMode.EMBEDDINGS:
        return AzureOpenAIEmbeddings(
            azure_deployment=azure_openai_deployment,
            api_version=azure_openai_api_version,
            api_key=azure_openai_api_key,
            max_retries=max_retries,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")
