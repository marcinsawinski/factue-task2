from enum import Enum


class Job(str, Enum):
    PERSUASION = "persuasion"
    NORMALIZATION = "normalization"


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
    LLAMA_32_3B = "llama3.2:3b"
    LLAMA_32_3B_Q4KM = "llama3.2:3b-instruct-q4_K_M"
    LLAMA_32_3B_Q8 = "llama3.2:3b-instruct-q8_0"
    LLAMA_PLLUM_8B = "antoniprzybylik/llama-pllum:8b"
    DEEPSEEK_R1_8B = "deepseek-r1:8b"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_41_MINI_FT1 = "gpt-4-1-mini-2025-04-14-ft-persuasion-detect-v1"
    GPT_41_MINI_FT2_11 ="gpt-4-1-mini-2025-04-14-ft-pers_v2_r11"
    GPT_41_MINI_FT2_21 ="gpt-4-1-mini-2025-04-14-ft-pers_v2_r21"
    GPT_41_MINI_FT2_31 ="gpt-4-1-mini-2025-04-14-ft-pers_v2_r31"
    GPT_41 = "gpt-4.1"
    GPT_4O = "gpt-4o"
    O4_MINI = "o4-mini"
    DEFAULT = "deafault"

    @classmethod
    def key_of(cls, value):
        for key, val in vars(cls).items():
            if not key.startswith("__") and val == value:
                return key.lower()
        return "UNKNOWN".lower()
