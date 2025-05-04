from enum import Enum


class Job(str, Enum):
    PERSUASION = "persuasion"
    NORMALIZE = "normalize"


class ModelMode(str, Enum):
    CHAT = "chat"
    LLM = "llm"
    EMBEDDINGS = "embeddings"


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    LMS = "lms"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    VLLM = "vllm"


class ModelName(str, Enum):
    LLAMA_31_8B = "llama3.1:8b"
    DEEPSEEK_R1_8B = "deepseek-r1:8b"
    GPT_4O_MINI = "gpt-4o-mini"
    DEFAULT = "deafault"

    @classmethod
    def key_of(cls, value):
        for key, val in vars(cls).items():
            if not key.startswith("__") and val == value:
                return key.lower()
        return "UNKNOWN".lower()
