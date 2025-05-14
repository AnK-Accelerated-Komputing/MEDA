"""Testing the multi-agent CAD generation system with batch processing
Agents are:
1. User
2. Design Expert
3. CAD Coder
4. Executor
5. Script_Execution_Reviewer"""
import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime

from autogen import GroupChat, GroupChatManager
from autogen.agentchat.utils import gather_usage_summary
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
from MEDA.create_agents import create_mechdesign_agents

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
        "Flush"
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
    """Multi agent CAD generation with batch processing"""
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"tests/results/test_script_exec_reviewer_log{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    # Set the working directory for CAD generation
    cad_working_dir=f"tests/results/test_script_exec_reviewer_CAD_{timestamp}"

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
        agents_list = create_mechdesign_agents(config,cad_working_dir,system_message_path="tests/system_message/custom_sys_msg_script_execution_reviewer.yaml")
        meda = [agents_list[0], #user
                       agents_list[1], #design expert
                       agents_list[2], #cad coder
                       agents_list[3], #executor
                        agents_list[4],] #reviewer
        graph_dict = {}
        graph_dict[agents_list[0]] = [agents_list[1]]
        graph_dict[agents_list[1]] = [agents_list[2]]
        graph_dict[agents_list[2]] = [agents_list[3]]
        graph_dict[agents_list[3]] = [agents_list[4]]
        graph_dict[agents_list[4]] = [agents_list[1],agents_list[2]]
        
        groupchat = GroupChat(
            agents=meda,
            messages=[],
            max_round=8, #8 for 1 refinement, 12 for 2 refinements
            # speaker_selection_method="round_robin",
            speaker_selection_method="auto",
            # allow_repeat_speaker=False,
            func_call_filter=True,
            select_speaker_auto_verbose=False,
            send_introductions=True,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            speaker_transitions_type="allowed",
        )
        group_chat_manager = GroupChatManager(
            groupchat=groupchat, llm_config={"seed":25,
                "temperature":0.3,
                "config_list": [config]})
        all_agents = meda.copy()
        all_agents.append(group_chat_manager)
        print("\nBatch CAD generation system")
        print("----------------------------------")
        try:
            filename = "data/cad_prompts.txt"
            prompts = read_prompts_from_file(filename)
            for agent in meda:
                agent.reset()
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
                    for agent in meda:
                        agent.reset()
                    print(
                        f"\nProcessing prompt {i} of {len(prompts)}: {prompt}")
                    start = time.time()
                    response = meda[0].initiate_chat(
                        group_chat_manager, message=prompt)
                    processing_time = time.time() - start
                    response_cost = gather_usage_summary(all_agents)
                    usage_metrics = extract_usage_metrics(response_cost)

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
