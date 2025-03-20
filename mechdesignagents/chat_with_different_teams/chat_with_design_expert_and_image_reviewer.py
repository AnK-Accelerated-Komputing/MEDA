"Testing with image reviewer"
import os
import re
import sys

from autogen import GroupChat, GroupChatManager
from autogen.agentchat.contrib.capabilities.vision_capability import \
    VisionCapability

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(root_dir)
from mechdesignagents.agents import *


def multimodal_designers_chat(design_problem: str):
    """
    Creates a group chat environment for collaborative design problem solving.

    Args:
        design_problem (str): The design problem to be discussed.

    Required Agents:
        - designer
        - design_expert
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
    design_problem = re.sub(
        r'(\S+\.(?:jpg|jpeg|png|gif|bmp))',
        r'<img \1>',
        design_problem,
        flags=re.IGNORECASE)
    reset_agents()
    groupchat = GroupChat(
        # agents=[User,designer_expert,cad_coder, executor, reviewer,cad_data_reviewer],
        agents=[User, design_expert, cad_coder, executor, reviewer,cad_image_reviewer],
        messages=[],
        max_round=20,
        # speaker_selection_method="round_robin",
        speaker_selection_method="auto",
        allow_repeat_speaker=False,
        func_call_filter=True,
        select_speaker_auto_verbose=False,
        send_introductions=True,
        # allowed_or_disallowed_speaker_transitions=allowed_transitions,
        # speaker_transitions_type="allowed"
    )
    vision_capability = VisionCapability(lmm_config=llm_config)
    group_chat_manager = GroupChatManager(
        groupchat=groupchat, llm_config=llm_config)
    vision_capability.add_to_agent(group_chat_manager)

    rst = User.initiate_chat(
        group_chat_manager,
        message=design_problem,
    )
    print(rst.cost)


def main():
    """Main function for running the CAD design chat system."""
    print("\nCAD Design Assistant")
    print("-------------------")
    print("Enter 'exit' to exit the program")

    while True:
        try:
            prompt = input(
                "\nEnter your design problem (or 'exit'if you want to exit): ")
            if prompt.lower() == 'exit':
                print("\nExiting CAD Design Assistant")
                break
            multimodal_designers_chat(prompt)

        except KeyboardInterrupt:
            print("\nSession interrupted by user")
            break
        except ValueError as ve:
            print(f"\nError: {str(ve)}")
            print("Please try again with a more detailed prompt")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again or create github issues if the problem persists")


if __name__ == "__main__":
    main()
