"Return the path to an STL and python file mentioned in the chat history."
import re


def file_path_finder(chat_history):
    """
    Finds the paths to STL and Python (.py) files mentioned in the chat history.

    Args:
        chat_history (list): A list of dictionaries representing the chat history.
                             Each dictionary should have 'name' and 'content' keys.

    Returns:
        dict: A dictionary containing the full paths to the STL and Python files if found.
    """
    stl_filename = None
    py_filename = None

    for entry in chat_history:
        if entry['name'] == 'CAD_Script_Writer':
            # Find STL filename
            stl_match = re.search(r'"([^"]+\.stl)"', entry['content'])
            if stl_match:
                stl_filename = stl_match.group(1)

            # Find Python filename
            py_match = re.search(r'([\w\d_-]+\.py)', entry['content'])
            if py_match:
                py_filename = py_match.group(1)

    # Define the base path
    base_path = './NewCADs'

    # Construct full paths
    file_paths = {}
    if stl_filename:
        file_paths['stl'] = f"{base_path}/{stl_filename}"
    if py_filename:
        file_paths['py'] = f"{base_path}/{py_filename}"

    return file_paths if file_paths else None
