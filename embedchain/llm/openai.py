from typing import Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from embedchain.config import BaseLlmConfig
from embedchain.helper.json_serializable import register_deserializable
from embedchain.llm.base import BaseLlm


@register_deserializable
class OpenAILlm(BaseLlm):
    def __init__(self, config: Optional[BaseLlmConfig] = None):
        super().__init__(config=config)

    def get_llm_model_answer(self, prompt):
        response = OpenAILlm._get_answer(prompt, self.config)

        if self.config.stream:
            return response
        else:
            return response.content

    def _get_answer(prompt: str, config: BaseLlmConfig) -> str:
        messages = []
        if config.system_prompt:
            messages.append(SystemMessage(content=config.system_prompt))
        messages.append(HumanMessage(content=prompt))
        kwargs = {
            "model": config.model or "gpt-3.5-turbo",
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "model_kwargs": {},
        }
        if config.top_p:
            kwargs["model_kwargs"]["top_p"] = config.top_p
        if config.stream:
            from langchain.callbacks.streaming_stdout import \
                StreamingStdOutCallbackHandler

            chat = ChatOpenAI(**kwargs, streaming=config.stream, callbacks=[StreamingStdOutCallbackHandler()])
        else:
            chat = ChatOpenAI(**kwargs)
        return chat(messages)
