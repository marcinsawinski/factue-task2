import requests
from langchain_ollama import ChatOllama, OllamaEmbeddings, OllamaLLM

from factue.utils.types import ModelMode
from factue.utils.vars import ollama_host

DEFAULT_MODEL = "llama3.2:latest"

base_url = f"http://{ollama_host}"


def init_ollama(
    base_url=base_url,
    model=DEFAULT_MODEL,
    mode=ModelMode.CHAT,
    temperature=0.0,
    seed=-1,
    num_predict=1000,
):
    url = f"{base_url}/api/tags"
    response = requests.get(url)
    models = response.json()["models"]
    model_names = [model["name"] for model in models]
    if model not in model_names:
        model = model_names[0]

    if mode == ModelMode.CHAT:
        return ChatOllama(
            base_url=base_url,
            model=model,
            keep_alive="60s",
            # temperature=temperature,
            seed=seed,
            num_predict=num_predict,
        )
    elif mode == ModelMode.LLM:
        return OllamaLLM(
            base_url=base_url,
            model=model,
            keep_alive="60s",
            # temperature=temperature,
            seed=seed,
            num_predict=num_predict,
        )
    elif mode == ModelMode.EMBEDDINGS:
        return OllamaEmbeddings(
            base_url=base_url,
            model=model,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")


def get_ollama_models(base_url=base_url):
    url = f"{base_url}/api/tags"
    response = requests.get(url)
    models = response.json()["models"]
    import pandas as pd

    return pd.json_normalize(models).drop(
        columns=["modified_at", "digest", "details.parent_model", "details.families"]
    )
