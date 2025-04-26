import os

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL")
DUMMY = SecretStr("DUMMY")


def init_vllm(base_url=VLLM_BASE_URL, model=None, streaming=False):

    if model is None:
        response = requests.get(base_url + "/models")  # type: ignore
        model = str(response.json()["data"][0]["id"])

    return ChatOpenAI(
        base_url=base_url,  # Your local vLLM endpoint
        model=model,  # Model name from the vLLM server
        api_key=DUMMY,  # Just a placeholder
        streaming=streaming,
        # callbacks=[StreamingStdOutCallbackHandler()]
    )
