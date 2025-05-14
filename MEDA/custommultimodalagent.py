"""Custom multimodal conversable agent."""
from typing import Optional, Union

from autogen.agentchat.agent import Agent
from autogen.agentchat.contrib.img_utils import message_formatter_pil_to_b64
from autogen.agentchat.contrib.multimodal_conversable_agent import \
    MultimodalConversableAgent
from autogen.oai.client import OpenAIWrapper

DEFAULT_LMM_SYS_MSG = """You are a helpful AI assistant."""
DEFAULT_MODEL = "gpt-4-vision-preview"


class CustomMultimodalConversableAgent(MultimodalConversableAgent):
    """Custom multimodal conversable agent."""

    def __init__(
            self,
            name: str,
            system_message: Optional[Union[str, list]] = "",
            is_termination_msg: str = None,
            *args,
            **kwargs,
    ):
        super().__init__(
            name,
            system_message,
            is_termination_msg=is_termination_msg,
            *args,
            **kwargs,
        )
        self.replace_reply_func(
            MultimodalConversableAgent.generate_oai_reply,
            CustomMultimodalConversableAgent.generate_oai_reply,
        )

    def generate_oai_reply(
            self,
            messages: Optional[list[dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[OpenAIWrapper] = None,
    ) -> tuple[bool, Union[str, dict, None]]:
        """Generate a reply using autogen.oai."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]

        # Custom modifications ##################################################
        new_messages = []
        for message in messages:
            if message["role"] != "tool":
                new_messages.append(message)
            else:
                for sub_message in message["tool_responses"]:
                    new_messages.append(sub_message)
        messages = new_messages
        #####################################################################

        messages_with_b64_img = message_formatter_pil_to_b64(
            self._oai_system_message + messages)
        response = client.create(
            context=messages[-1].pop("context", None), messages=messages_with_b64_img)
        extracted_response = client.extract_text_or_completion_object(response)[
            0]
        if not isinstance(extracted_response, str):
            extracted_response = extracted_response.model_dump()
        return True, extracted_response
