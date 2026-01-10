import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
import prompts
import config
import functions.get_files_info
from call_function import available_functions


def main():

    load_dotenv() 

    api_key =  os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise RuntimeError("Api Key is empty or failed to retrieve")
    else:
        print("API key loaded")
        client = genai.Client(api_key=api_key)
        print("client made")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose",action="store_true",help="Enable verbose output")
    args = parser.parse_args()
    # Now we can access `args.user_prompt`

    request = args.user_prompt
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=prompts.system_prompt,
            temperature=0,
            tools=[available_functions])
        )
    
    if args.verbose:
        print(f"User prompt: {request}")
        if response.usage_metadata == None:
            raise RuntimeError("response Metadata empty")
        else:
            # number of tokens in the prompt that was sent to the model:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            # number of tokens in the model's response:
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
    

    print("Response:")
    response_lines = []
    if response.function_calls:
        for function_call in response.function_calls:
            response_lines.append(f"Calling function: {function_call.name}({function_call.args})")
        print("\n".join(response_lines))
    else:      
        print(response.text)
    


if __name__ == "__main__":
    main()
