from factue.utils.types import ModelMode, ModelProvider


class Llm:
    def __init__(self, model_name: str, provider, mode: str = "chat", **kwargs):
        self.provider = provider
        self.model_name = model_name
        self.mode = mode
        self.kwargs = kwargs
        if self.provider == ModelProvider.OLLAMA:
            from factue.methods.llm_langchain.ollama import init_ollama

            self.model = init_ollama(
                model=self.model_name, mode=ModelMode(self.mode), **self.kwargs
            )
        elif provider == ModelProvider.AZURE_OPENAI:
            from factue.methods.llm_langchain.azure_openai import \
                init_azure_openai

            self.model = init_azure_openai(mode=ModelMode(self.mode), **self.kwargs)
        elif provider == ModelProvider.OPENAI:
            from factue.methods.llm_langchain.openai import init_openai

            self.model = init_openai(
                model=self.model_name, mode=ModelMode(self.mode), **self.kwargs
            )
        elif provider == ModelProvider.LMS:
            from factue.methods.llm_langchain.lms import init_lms

            self.model = init_lms(
                model=self.model_name, mode=ModelMode(self.mode), **self.kwargs
            )
        elif provider == ModelProvider.VLLM:
            from factue.methods.llm_langchain.vllm import init_vllm

            self.model = init_vllm(model=self.model_name, **self.kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def __getattr__(self, name):
        """Forward any unknown attribute to self.model"""
        return getattr(self.model, name)
