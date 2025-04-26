import requests
from langchain_openai import ChatOpenAI

VLLM_BASE_URL = "http://localhost:8000/v1"


def init_vllm(base_url=VLLM_BASE_URL, model=None, streaming=False):
    if model is None:
        response = requests.get(base_url + "/models")
        model = str(response.json()["data"][0]["id"])

    return ChatOpenAI(
        base_url=base_url,  # Your local vLLM endpoint
        model=model,  # Model name from the vLLM server
        api_key="not-needed",  # Just a placeholder
        streaming=streaming,
        # callbacks=[StreamingStdOutCallbackHandler()]
    )
