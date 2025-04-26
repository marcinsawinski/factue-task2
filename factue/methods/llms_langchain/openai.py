from langchain_openai import ChatOpenAI, OpenAIEmbeddings, OpenAI

import lmstudio as lms
import pandas as pd
from factue.methods.llms_langchain.model_mode import ModelMode
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

DEFAULT_MODEL = "gpt-4o-mini"


def init_openai(
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

            api_key=openai_api_key,
            model=model,
            streaming=streaming,
            temperature=temperature,
            max_retries=max_retries,
        )
    elif mode == ModelMode.LLM:
        return OpenAI(

            api_key=openai_api_key,
            model=model,
            streaming=streaming,
            temperature=temperature,
            max_retries=max_retries,
        )
    elif mode == ModelMode.EMBEDDINGS:
        return OpenAIEmbeddings(
            api_key=openai_api_key,
            model=model,
            temperature=temperature,
            max_retries=max_retries,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")


def get_openai_models():
    from openai import OpenAI as base_OpenAI

    with base_OpenAI(api_key=openai_api_key) as client:
        models = client.models.list()
        model_dicts = [model.to_dict() for model in models]
        df = pd.json_normalize(model_dicts)
        df['created'] = pd.to_datetime(df['created'], unit='s', utc=True)
        return df