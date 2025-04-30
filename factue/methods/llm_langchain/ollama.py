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
    seed=0,

):
    url = f"{base_url}/api/tags"
    response = requests.get(url)
    models = response.json()["models"]
    model_names = [model["name"] for model in models]
    if model not in model_names:
        model = model_names[0]

    if mode == ModelMode.CHAT:
        print("seed: ",seed)
        return ChatOllama(
            base_url=base_url,
            model=model,
            keep_alive="30s",
            temperature=temperature,
            model_kwargs={"seed": seed}
            # num_predict=100,
        )
    elif mode == ModelMode.LLM:
        return OllamaLLM(
            base_url=base_url,
            model=model,
            keep_alive="30s",
            temperature=temperature,
            # num_predict=100,
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
