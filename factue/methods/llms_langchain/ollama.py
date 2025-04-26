import requests
from langchain_ollama import ChatOllama, OllamaEmbeddings, OllamaLLM

from factue.methods.llms_langchain.model_mode import ModelMode

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:latest"


def init_ollama(
    base_url=OLLAMA_BASE_URL, model=DEFAULT_MODEL, streaming=False, mode=ModelMode.CHAT
):
    url = f"{base_url}/api/tags"
    response = requests.get(url)
    models = response.json()["models"]
    model_names = [model["name"] for model in models]
    if model not in model_names:
        model = model_names[0]

    if mode == ModelMode.CHAT:
        return ChatOllama(
            base_url=base_url, model=model, keep_alive="30s", streaming=streaming
        )
    elif mode == ModelMode.LLM:
        return OllamaLLM(
            base_url=base_url, model=model, keep_alive="30s", streaming=streaming
        )
    elif mode == ModelMode.EMBEDDINGS:
        return OllamaEmbeddings(base_url=base_url, model=model)
    else:
        raise ValueError(f"Invalid mode: {mode}")


def get_ollama_models(base_url=OLLAMA_BASE_URL):
    url = f"{base_url}/api/tags"
    response = requests.get(url)
    models = response.json()["models"]
    import pandas as pd

    return pd.json_normalize(models).drop(
        columns=["modified_at", "digest", "details.parent_model", "details.families"]
    )
