import os
import sys

from autogen import GroupChat, GroupChatManager

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
print(root_dir)
sys.path.append(root_dir)
from mechdesignagents.agents import *


def designers_chat(design_problem: str):
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
    reset_agents()
    groupchat = GroupChat(
        agents=[User, designer_expert, cad_coder, executor, reviewer],
        messages=[],
        max_round=50,
        # speaker_selection_method="round_robin",
        speaker_selection_method="auto",
        allow_repeat_speaker=False,
        func_call_filter=True,
        select_speaker_auto_verbose=False,
        send_introductions=True,
        # allowed_or_disallowed_speaker_transitions=allowed_transitions,
        # speaker_transitions_type="allowed"
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the designer as this is the user proxy agent.
    response = User.initiate_chat(
        manager,
        message=design_problem,
    )
    print(response.cost)


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
            designers_chat(prompt)

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
