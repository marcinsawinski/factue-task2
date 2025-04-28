import lmstudio as lms
import pandas as pd
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from pydantic import SecretStr

from factue.utils.types import ModelMode

LMS_BASE_URL = "http://localhost:1234/v1"
DEFAULT_MODEL = "llama3.2:latest"
DUMMY = SecretStr("DUMMY")


def init_lms(
    base_url=LMS_BASE_URL,
    model=DEFAULT_MODEL,
    streaming=False,
    mode=ModelMode.CHAT,
    temperature=0.0,
    max_retries=2,
):
    with lms.Client() as client:
        loaded_models = client.list_loaded_models()
        loaded_model_names = [model.identifier for model in loaded_models]
        if model not in loaded_model_names:
            model = loaded_model_names[0]

    if mode == ModelMode.CHAT:
        return ChatOpenAI(
            base_url=base_url,
            api_key=DUMMY,
            model=model,
            streaming=streaming,
            temperature=temperature,
            max_retries=max_retries,
        )
    elif mode == ModelMode.LLM:
        return OpenAI(
            base_url=base_url,
            api_key=DUMMY,
            model=model,
            streaming=streaming,
            temperature=temperature,
            max_retries=max_retries,
        )
    elif mode == ModelMode.EMBEDDINGS:
        return OpenAIEmbeddings(
            base_url=base_url,
            api_key=DUMMY,
            model=model,
            max_retries=max_retries,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")


def _model_to_dict(m):
    return {
        "type": "embedding" if isinstance(m, lms.EmbeddingModelInfo) else "llm",
        "model_key": getattr(m, "model_key", None),
        "display_name": getattr(m, "display_name", None),
        "format": getattr(m, "format", None),
        "architecture": getattr(m, "architecture", None),
        "size_bytes": getattr(m, "size_bytes", None),
        "path": getattr(m, "path", None),
        "vision": getattr(m, "vision", None),
        "trained_for_tool_use": getattr(m, "trained_for_tool_use", None),
        "max_context_length": getattr(m, "max_context_length", None),
        "params_string": getattr(m, "params_string", None),
    }


def get_models():

    with lms.Client() as client:
        downloaded_models = client.list_downloaded_models()
        loaded_models = client.list_loaded_models()
        loaded_model_names = [model.identifier for model in loaded_models]

        downloaded_dicts = [model.__dict__.get("_data") for model in downloaded_models]
        model_dicts = [_model_to_dict(m) for m in downloaded_dicts]
        model_dicts = [
            {**model, "loaded": model["model_key"] in loaded_model_names}
            for model in model_dicts
        ]
        return pd.DataFrame(model_dicts)
