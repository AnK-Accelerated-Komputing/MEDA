
"""Batch CAD generation system using two agents:
1. User
2. CadQuery Code Writer"""
import os
import sys
import time
import json
from datetime import datetime
from contextlib import contextmanager

from autogen import AssistantAgent, UserProxyAgent


class TeeStream:
    """Stream object that writes to both terminal and file"""

    def __init__(self, filename, stream):
        self.terminal = stream
        self.file = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        "Write the message to both terminal and file"
        self.terminal.write(message)
        self.file.write(message)
        self.file.flush()

    def flush(self):
        "Flush the stream"
        self.terminal.flush()
        self.file.flush()


@contextmanager
def tee_output(filename):
    """Context manager to temporarily redirect stdout and stderr to both terminal and file"""
    stdout_tee = TeeStream(filename, sys.stdout)
    stderr_tee = TeeStream(f"{filename}", sys.stderr)

    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = stdout_tee, stderr_tee

    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        stdout_tee.file.close()
        stderr_tee.file.close()


def read_prompts_from_file(filename):
    """Read and extract prompts from the specified file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except (OSError, IOError) as e:
        print(f"Error reading file: {str(e)}")
        return []


def extract_usage_metrics(response_cost):
    """Extract detailed usage metrics from response cost"""
    total_cost = response_cost['usage_including_cached_inference']['total_cost']
    model_usage = response_cost['usage_including_cached_inference']['gpt-4o-2024-08-06']

    return {
        'total_cost': total_cost,
        'prompt_tokens': model_usage['prompt_tokens'],
        'completion_tokens': model_usage['completion_tokens'],
        'total_tokens': model_usage['total_tokens']
    }


def save_results(results, filename):
    """Save results to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


def main():
    """Two agent CAD generation with batch processing"""
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"cad_generation_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    # Files for logging
    log_file = os.path.join(output_dir, "terminal_output.log")
    results_file = os.path.join(output_dir, "results.json")

    with tee_output(log_file):
        print(f"\nStarting CAD generation at {timestamp}")
        print("Output directory:", output_dir)

        # [Your existing configuration code here...]
        config = {
            "model": "gpt-4o-0806",
            "api_key": os.environ["AZURE_API_KEY"],
            "base_url": os.environ["AZURE_OPENAI_BASE"],
            "api_type": "azure",
            "api_version": "2024-08-01-preview"
        }

        llm_config = {
            "seed": 25,
            "temperature": 0.3,
            "config_list": [config],
        }

        def termination_msg(x):
            "Terminate the chat for the given agent"
            return isinstance(x, dict) and "TERMINATE" == str(
                x.get("content", ""))[-9:].upper()

        user = UserProxyAgent(
            name="User",
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={
                "work_dir": "GPT_single_5",
                "use_docker": False,
            },
            description="The designer who asks questions to create CAD models using CadQuery",
        )

        cad_coder = AssistantAgent(
            "CAD_Script_Writer",
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
            Only use CadQuery’s predefined shapes and operations""",
            llm_config=llm_config,
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            description="""CadQuery Code Writer who writes python code to
              create CAD models following the system message.""",
        )

        print("\nBatch CAD generation system")
        print("----------------------------------")
        try:
            filename = "tests/prompts.txt"
            prompts = read_prompts_from_file(filename)

            if not prompts:
                print("No prompts found in file. Exiting.")
                return

            print(f"Found {len(prompts)} prompts to process")
            results = []

            total_metrics = {
                'total_cost': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0
            }

            for i, prompt in enumerate(prompts, 1):
                try:
                    print(
                        f"\nProcessing prompt {i} of {len(prompts)}: {prompt}")

                    cad_coder.reset()
                    user.reset()

                    start = time.time()
                    response = user.initiate_chat(
                        cad_coder, message=prompt, max_turns=5)
                    processing_time = time.time() - start
                    print(response.cost)
                    usage_metrics = extract_usage_metrics(response.cost)

                    for key in total_metrics:
                        total_metrics[key] += usage_metrics[key]

                    # Save result for this prompt
                    prompt_result = {
                        'prompt_number': i,
                        'prompt': prompt,
                        'time': processing_time,
                        'response': response.chat_history,  # Save the actual response
                        **usage_metrics
                    }
                    results.append(prompt_result)

                    # Save results after each prompt (in case of interruption)
                    save_results(results, results_file)

                    print(f'Time: {processing_time:.2f} seconds')
                    print(f'Cost: ${usage_metrics["total_cost"]:.6f}')
                    print(f"""Tokens: {usage_metrics["total_tokens"]}
                        (Prompt: {usage_metrics["prompt_tokens"]},
                        Completion: {usage_metrics["completion_tokens"]})""")

                except (OSError, ValueError, RuntimeError) as e:
                    error_msg = f"Error processing prompt {i}: {str(e)}"
                    print(error_msg)
                    results.append({
                        'prompt_number': i,
                        'prompt': prompt,
                        'error': str(e)
                    })
                    save_results(results, results_file)

            # Print and save final summary
            print("\nProcessing Summary:")
            print(f"Total prompts processed: {len(results)}")

            successful = sum(1 for r in results if 'error' not in r)
            print(f"Successful: {successful}")
            print(f"Failed: {len(results) - successful}")

            if successful > 0:
                total_time = sum(r['time']
                                 for r in results if 'error' not in r)
                print("\nTime Statistics:")
                print(f"Total processing time: {total_time:.2f} seconds")
                print(f"""Average processing time: {
                      total_time/successful:.2f} seconds""")

                print("\nCost Statistics:")
                print(f"Total cost: ${total_metrics['total_cost']:.6f}")
                print(f"""Average cost per prompt: ${
                      total_metrics['total_cost']/successful:.6f}""")

                print("\nToken Usage Statistics:")
                print(f"Total tokens: {total_metrics['total_tokens']}")
                print(f"Total prompt tokens: {total_metrics['prompt_tokens']}")
                print(f"""Total completion tokens: {
                      total_metrics['completion_tokens']}""")
                print(f"""Average tokens per prompt: {
                      total_metrics['total_tokens']/successful:.1f}""")

        except KeyboardInterrupt:
            print("\nSession interrupted by user")
        except (OSError, ValueError) as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again or create github issues if the problem persists")


if __name__ == "__main__":
    main()
