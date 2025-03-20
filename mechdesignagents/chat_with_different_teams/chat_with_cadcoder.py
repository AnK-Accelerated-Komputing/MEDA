import os
import sys

from autogen import AssistantAgent, UserProxyAgent
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
print(root_dir)
sys.path.append(root_dir)
from mechdesignagents.agents import *


# for two agent system with just designer and cad coder.

User = UserProxyAgent(
    name="User",
    is_termination_msg=termination_msg,
    human_input_mode="Never",  # Use ALWAYS for human in the loop
    # Change it to limit the number of replies from this agent
    max_consecutive_auto_reply=1,
    # here we define the coding configuration for executing the code generated
    # by agent
    code_execution_config={
        "work_dir": "mechdesignagents/NewCADs",
        "use_docker": False,
    },
    # llm_config={"config_list": config_list}, #you can also select a
    # particular model from the config list here for llm
    system_message=""" A human designer who asks questions to create CAD models using CadQuery. You execute
    the python code written by CAD code writer. Terminate after successful cad model creation """,
    description="The designer who asks questions to create CAD models using CadQuery",
)

cad_coder = AssistantAgent(
    "CadQuery Code Writer",
    system_message="""You only create the CAD model requested by the User.
    You write python code to create CAD models using CadQuery.
    Wrap the code in a code block that specifies the script type.
    The user can't modify your code.
    So do not suggest incomplete code which requires others to modify.
    Don't use a code block if it's not intended to be executed by the executor.
    Don't include multiple code blocks in one response.
    Do not ask others to copy and paste the result.
    If the result indicates there is an error, fix the error and output the code again.
    Suggest the full code instead of partial code or code changes.
    For every response, use this format in Python markdown:
        Adhere strictly to the following outline
        Python Markdown and File Name
        Start with ```python and # filename: <design_name>.py (based on model type).

        Import Libraries
        ALWAYS import cadquery and ocp_vscode (for visualization).

        Define Parameters
        List dimensions or properties exactly as instructed by the analyst.

        Create the CAD Model
        Build models using only CadQuery’s primitives and boolean operations as directed.

        Save the Model
        Export in STL, STEP, and DXF formats.

        Visualize the Model
        Use show(model_name) from ocp_vscode to visualize.

        Example:
```
        python
        # filename: box.py
        import cadquery as cq
        from ocp_vscode import * #never forget this line

        # Step 1: Define Parameters
        height = 60.0
        width = 80.0
        thickness = 10.0

        # Step 2: Create the CAD Model
        box = cq.Workplane("XY").box(height, width, thickness)

        # Step 3: Save the Model
        cq.exporters.export(box, "box.stl")
        cq.exporters.export(box.section(), "box.dxf")
        cq.exporters.export(box, "box.step")

        # Step 4: Visualize the Model
        show(box) #always visualize the model
```
        Only use CadQuery’s predefined shapes and operations based on the analyst’s instructions. And terminate after succesful creation of CAD model.
        """,
    llm_config=llm_config,
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    description="CadQuery Code Writer who writes python code to create CAD models following the system message.",
)


def chat_cad_coder(prompt: str):
    '''Chat with cad_coder agent.'''
    cad_coder.reset()
    User.reset()
    response = User.initiate_chat(cad_coder, message=prompt)
    print(response.cost)


def main():
    """Two agent CAD generation"""
    print("\nTwo agent CAD generation system")
    print("----------------------------------")
    print("Enter 'quit' to exit the program")

    reset_agents()

    while True:
        try:
            prompt = input(
                "\nEnter your design problem (or 'exit'if you want to exit): ")
            if prompt.lower() == 'exit':
                print("\nExiting CAD Design Assistant")
                break
            cad_coder.reset()
            User.reset()
            response = User.initiate_chat(cad_coder, message=prompt)
            while True:
                ask_next = input("Continue Chat or enter exit to exit: ")
                if ask_next.lower() == 'exit':
                    break
                User.send(recipient=cad_coder, message=ask_next)
            print(response.cost)

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
