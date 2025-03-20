import os
import sys

from autogen import GroupChat, GroupChatManager

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(root_dir)
from mechdesignagents.agents import *


def norag_chat(design_prblem: str):
    reset_agents()
    groupchat = GroupChat(
        agents=[User, cad_coder, reviewer,],
        messages=[],
        max_round=12,
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False,
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the designer as this is the user proxy agent.
    response = User.initiate_chat(
        manager,
        message=design_prblem,
    )
    print(response.cost)


def main():
    print("\nLet's create CAD models!")
    print("-------------------")
    print("Enter 'exit' to exit the program")

    while True:
        try:
            prompt = input(
                "\nEnter your design problem (or 'exit'if you want to exit): ")
            if prompt.lower() == 'exit':
                print("\nExiting CAD Design Assistant")
                break
            norag_chat(prompt)

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
