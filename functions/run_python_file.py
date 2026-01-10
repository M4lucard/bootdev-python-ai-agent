import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=None):

    try:
    
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # Will be True or False
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if file_path[-3:] != ".py":
            return f'Error: "{file_path}" is not a Python file'
        command = ["python", os.path.abspath(target_file)]
        if args:
            command.extend(args)
            
        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text = True,
            timeout = 30)

        lines = []

        if result.returncode != 0:
            lines.append(f"Process exited with code {result.returncode}")
        
        if not result.stdout and not result.stderr:
            lines.append("No output produced")
        else:
            if result.stdout:
                lines.append(f"STDOUT: {result.stdout}")
            if result.stderr:
                lines.append(f"STDERR: {result.stderr}")

        output = "\n".join(lines)

        return output

    except Exception as e:
        return f"Error: executing Python file: {e}"

# Define how LLM can use the function above
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a python file give a file path and optional arguments",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="file path to the python script to run",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items = types.Schema(type=types.Type.STRING),
                description="array of arguments to be given with the python script execution"
            ),
        },
        required=["file_path"],

    ),
)