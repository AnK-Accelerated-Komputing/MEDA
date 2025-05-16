"""
This module defines various agents for CAD model creation and management.
"""
import yaml
from autogen import AssistantAgent, UserProxyAgent
from typing_extensions import Annotated
from autogen.agentchat.contrib.multimodal_conversable_agent import \
    MultimodalConversableAgent
from utils.get_image_info import get_image_info


def get_system_message(agent,system_message_path="config/system_message.yaml"):
    """Return system message for the agent"""
    with open(system_message_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    system_message = config[agent]['system_message']
    return system_message

def create_mechdesign_agents(config, working_dir="NewCADs", system_message_path="config/system_message.yaml"):
    """
    Create the agents for the mechanical design task.

    Args:
        config(list): List of configurations for the agents.

    Returns:
        tuple: A tuple containing the created agents.
    """
    llm_config = {
        "seed": 50,
        "temperature": 0.3,
        "config_list": [config],
        # "request_timeout": 600,
        # "retry_wait_time": 120,
    }

    def termination_msg(x):
        "Terminate the chat for the given agent"
        return isinstance(x, dict) and "TERMINATE" == str(
            x.get("content", ""))[-9:].upper()

    user = UserProxyAgent(
        name="User",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",  # Use ALWAYS for human in the loop
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
        code_execution_config=False,
        system_message=get_system_message("User",system_message_path),
    )

    design_expert = AssistantAgent(
        name="Design_Expert",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",  # Use ALWAYS for human in the loop
        llm_config={
        "seed": 50,
        "temperature": 0.6,
        "config_list": [config],
    },
        system_message=get_system_message("Design_Expert",system_message_path),
        description="""The designer expert who provides approach to
    answer questions to create CAD models in CadQuery""",)


    cad_coder = AssistantAgent(
        "CAD_Script_Writer",
        system_message=get_system_message("CAD_Script_Writer",system_message_path),
        llm_config=llm_config,
        human_input_mode="NEVER",
        description="""CAD Script Writer who writes python code to
    create CAD models following the system message.""",)

    executor = AssistantAgent(
        name="Executor",
        is_termination_msg=termination_msg,
        system_message=get_system_message("Executor"),
        code_execution_config={
            "last_n_messages": 4,
            "work_dir": working_dir,
            "use_docker": False,
            "timeout": 20,
        },
        description="Executor who executes the code written by CAD Script Writer.")
    
    reviewer = AssistantAgent(
        name="Script_Execution_Reviewer",
        is_termination_msg=termination_msg,
        system_message=get_system_message("Script_Execution_Reviewer",system_message_path),
        llm_config=llm_config,
        description="""Code Reviewer who can review python code written
          by CAD Script Writer after executed by Executor.""",
    )

    cad_image_reviewer = AssistantAgent(
        name="CAD_Image_Reviewer",
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=llm_config,
        system_message=get_system_message("CAD_Image_Reviewer"),
        description="The CAD model image reviewer",
    )

    @cad_image_reviewer.register_for_execution()
    @cad_image_reviewer.register_for_llm(
        description="CAD model image reviewer")
    def call_image_reviewer(
        prompt: Annotated[str, "The prompt provided by the user to create the CAD model"]
    ) -> str:
        """This function returns message content from the response"""
        return get_image_info(prompt,working_dir)
    
    cad_data_reviewer = MultimodalConversableAgent(
        name="CAD_Data_Reviewer",
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=llm_config,
        system_message=get_system_message("CAD_Data_Reviewer"),
    )

    

    agents_list = [
        user,
        design_expert,
        cad_coder,
        executor,
        reviewer,
        cad_image_reviewer,
        cad_data_reviewer
    ]
    return agents_list
