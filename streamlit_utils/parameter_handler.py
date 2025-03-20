"Handles parameters in a python file"
import re
import os
import sys
import subprocess

class ParameterHandler:
    """
    A class to handle parameters in a Python file.
    """
    def __init__(self):
        self.param_pattern = r"([a-zA-Z_]+)\s*=\s*([0-9.]+)"
    
    def extract_parameters(self, python_file_path):
        "Extract parameters from a Python file"
        try:
            parameters = {}
            with open(python_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    match = re.search(self.param_pattern, line)
                    if match:
                        var_name = match.group(1)
                        var_value = float(match.group(2))
                        parameters[var_name] = var_value
            return parameters
        except (IOError, OSError):
            return {}

    def update_python_file(self, python_file_path, new_parameters):
        "Update parameters in a Python file"
        try:
            with open(python_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            for param_name, param_value in new_parameters.items():
                pattern = rf"({param_name}\s*=\s*)([-+]?\d*\.?\d+)"
                content = re.sub(pattern, rf"\g<1>{param_value}", content)

            with open(python_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except (IOError, OSError, subprocess.CalledProcessError):
            return False

    def execute_python_file(self, python_file_path):
        "Execute a Python file"
        try:
            file_directory = os.path.dirname(os.path.abspath(python_file_path))
            file_name = os.path.basename(python_file_path)
            original_directory = os.getcwd()
            
            try:
                os.chdir(file_directory)
                result = subprocess.run(
                    [sys.executable, file_name],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.returncode == 0
            finally:
                os.chdir(original_directory)
        except (subprocess.CalledProcessError, OSError):
            return False
