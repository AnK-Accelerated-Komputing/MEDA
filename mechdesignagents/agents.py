"""
This module defines various agents for CAD model creation and management.
"""
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import \
    MultimodalConversableAgent
# from autogen.agentchat.contrib.retrieve_user_proxy_agent import \
#     RetrieveUserProxyAgent
from typing_extensions import Annotated

from mechdesignagents.custommultimodalagent import \
    CustomMultimodalConversableAgent
from ptests.get_image_info import get_image_info
from utils.get_sys_msg import get_system_message
from utils.langchain_web import web_rag
from utils.llm import LLMConfigSelector

config_list_selection = LLMConfigSelector()
llm_config = {
    "seed": 25,
    "temperature": 0.3,
    "config_list": [config_list_selection.get_model_config()],
    # "request_timeout": 600,
    # "retry_wait_time": 120,
}


def termination_msg(x):
    "Terminate the chat for the given agent"
    return isinstance(x, dict) and "TERMINATE" == str(
        x.get("content", ""))[-9:].upper()


User = UserProxyAgent(
    name="User",
    is_termination_msg=termination_msg,
    human_input_mode="ALWAYS",  # Use ALWAYS for human in the loop
    max_consecutive_auto_reply=5,
    code_execution_config=False,
    system_message=get_system_message("User"),
    # description= "The designer who asks questions to create CAD models using CadQuery",
    # default_auto_reply="Reply `TERMINATE` if the task is done.",
)

functioncall_agent = AssistantAgent(
    name="Function_Call_Agent",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message=get_system_message("Function_Call_Agent"),
    description="The Function Call Agent that calls registered function to create cad models.")

design_expert = AssistantAgent(
    name="Design_Expert",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",  # Use ALWAYS for human in the loop
    # you can also select a particular model from the config list here for llm
    llm_config=llm_config,
    system_message=get_system_message("Design_Expert"),
    description="""The design expert who provides approach to
    answer questions to create CAD models in CadQuery""",)

# # Here we define our RAG agent.
# designer_aid = RetrieveUserProxyAgent(
#     name="Designer_Assistant",
#     is_termination_msg=termination_msg,
#     human_input_mode="NEVER",
#     llm_config=llm_config,
#     default_auto_reply="Reply `TERMINATE` if the task is done.",
#     code_execution_config=False,
#     retrieve_config={
#         "task": "code",
#         "docs_path": [
#             # change this to input any file you want for RAG
#             "/home/niel77/MechanicalAgents/data/code_documentation.pdf",
#         ],
#         "chunk_token_size": 500,
#         "collection_name": "groupchat",
#         "get_or_create": True,
#         "customized_prompt": '''You provide the relvant codes for creating 
#         the CAD models in CadQuery from the
#         documentation provided.''',
#     },
# )

cad_coder_assistant = AssistantAgent(
    name="CAD_coder_assistant",
    system_message=get_system_message("CAD_coder_assistant"),
    llm_config=llm_config,
    description="""The CAD coder assistant which uses function
    or tool call (calls call_rag function) to search the code 
    for cad model generation"""
)


@cad_coder_assistant.register_for_execution()
@cad_coder_assistant.register_for_llm(
    description="Code finder using Retrieval Augmented Generation")
def call_rag(
    question: Annotated[float, "Task for which code to be found"],
) -> str:
    """This function calls the RAG agent to find the code for the given task."""
    return web_rag(question)


cad_coder = AssistantAgent(
    "CadQuery_Code_Writer",
    system_message=get_system_message("CadQuery_Code_Writer"),
    llm_config=llm_config,
    human_input_mode="NEVER",
    description="""CadQuery Code Writer who writes python code to
    create CAD models following the system message.""",
)


executor = AssistantAgent(
    name="Executor",
    is_termination_msg=termination_msg,
    system_message=get_system_message("Executor"),
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "Multi_Image_Reviewer",
        "use_docker": False,
    },
    description="Executor who executes the code written by CadQuery Code Writer.")
reviewer = AssistantAgent(
    name="Reviewer",
    is_termination_msg=termination_msg,
    system_message=get_system_message("Reviewer"),
    llm_config=llm_config,
    description="""Code Reviewer who can review python code written by
    CadQuery Code Writer after executed by Executor.""",
)

cad_data_reviewer = MultimodalConversableAgent(
    name="CAD_Data_Reviewer",
    # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    code_execution_config=False,
    llm_config=llm_config,
    system_message=get_system_message("CAD_Data_Reviewer"),
)

cad_image_reviewer = CustomMultimodalConversableAgent(
        name="CAD_Image_Reviewer",
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=llm_config,
        system_message=get_system_message("CAD_Image_Reviewer"),
    )

@cad_image_reviewer.register_for_execution()
@cad_image_reviewer.register_for_llm(
    description="CAD model image reviewer")
def call_image_reviewer(
    prompt: Annotated[str, "The prompt provided by the user to create the CAD model"]
) -> str:
    """This function returns the path of the image to be reviewed by the CAD_Image_Reviewer."""
    return get_image_info(prompt)

def reset_agents():
    "Reset the agents"
    User.reset()
    # designer_aid.reset()
    cad_coder_assistant.reset()
    executor.reset()
    cad_coder.reset()
    reviewer.reset()
    design_expert.reset()
