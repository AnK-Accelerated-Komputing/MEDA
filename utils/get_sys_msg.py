"Return system message for the agent"
import yaml


def get_system_message(agent):
    """Return system message for the agent"""
    with open('/home/niel77/testmeda/MEDA/ptests/system_message/system_message_test_image_reviewer_cadprompt_function_call.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    system_message = config[agent]['system_message']
    return system_message
