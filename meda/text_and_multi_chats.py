"""
This module facilitates agentic chats for collaborative design problem solving.
This is specifically created for Streamlit app use.
"""
from autogen import GroupChat, GroupChatManager
from autogen.agentchat.contrib.capabilities.vision_capability \
    import VisionCapability
from utils.path_finder import file_path_finder
from utils.image_path_changer import update_image_path


def multimodal_designers_chat(agents, config, design_problem: str):
    """
    Creates a group chat environment for collaborative design problem solving.

    Args:
        design_problem (str): The design problem to be discussed.

    Required Agents:
        - designer
        - designer_expert
        - cad_coder
        - executor
        - reviewer
        - cad_reviewer

    Configuration:
        - max_round: 50
        - speaker_selection: round_robin
        - allow_repeat_speaker: False

    Example:
        >>> designers_chat("Design a water bottle")
    """
    # Replace image file paths with <img image_path>
    agents_list = agents
    design_problem = update_image_path(design_problem)
    # reset_agents()
    groupchat = GroupChat(
        # agents=[User,designer_expert,cad_coder, executor, reviewer,cad_data_reviewer],
        agents=agents_list,

        messages=[],
        max_round=50,
        # speaker_selection_method="round_robin",
        speaker_selection_method="auto",
        allow_repeat_speaker=False,
        func_call_filter=True,
        select_speaker_auto_verbose=False,
        send_introductions=True,
    )
    vision_capability = VisionCapability(lmm_config={"config_list": [config]})
    group_chat_manager = GroupChatManager(
        groupchat=groupchat, llm_config={"config_list": [config]})
    vision_capability.add_to_agent(group_chat_manager)

    rst = agents_list[0].initiate_chat(
        group_chat_manager,
        message=design_problem,
    )
    output = rst.chat_history
    return file_path_finder(output)


def designers_chat(agents, config, design_problem: str):
    """
    Creates a group chat environment for collaborative design problem solving.

    Args:
        design_problem (str): The design problem to be discussed.

    Required Agents:
        - designer
        - designer_expert
        - cad_coder
        - executor
        - reviewer

    Configuration:
        - max_round: 50
        - speaker_selection: round_robin
        - allow_repeat_speaker: False

    Example:
        >>> designers_chat("Design a water bottle")
    """
    agents_list = agents
    groupchat = GroupChat(
        agents=agents_list,
        messages=[],
        max_round=50,
        # speaker_selection_method="round_robin",
        speaker_selection_method="auto",
        allow_repeat_speaker=False,
        func_call_filter=True,
        select_speaker_auto_verbose=False,
        send_introductions=True,
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": [config]})

    # Start chatting with the designer as this is the user proxy agent.
    response = agents_list[0].initiate_chat(
        manager,
        message=design_problem,
    )
    output = response.chat_history
    return file_path_finder(output)