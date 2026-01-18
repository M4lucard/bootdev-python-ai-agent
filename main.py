import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
import prompts
import config
import functions.get_files_info
from call_function import available_functions, call_function


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
    
    for _ in range(20):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=prompts.system_prompt,
                temperature=0,
                tools=[available_functions])
            )
        
        # Add model candidates to the conversation
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

        if args.verbose:
            print(f"User prompt: {request}")
            if response.usage_metadata == None:
                raise RuntimeError("response Metadata empty")
            else:
                # number of tokens in the prompt that was sent to the model:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                # number of tokens in the model's response:
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        
        
        # response handling

        
        print("Response:")
        if response.function_calls:
            function_responses = []
            for function_call in response.function_calls:
                result = call_function(function_call, args.verbose)

                if not result.parts:
                    raise RuntimeError("Empty parts in function result")
                if result.parts[0].function_response is None:
                    raise RuntimeError("Missing function_response in function result")
                if result.parts[0].function_response.response is None:
                    raise RuntimeError("Missing response in function_response")

                if args.verbose:
                    print(f"-> {result.parts[0].function_response.response}")

                function_responses.append(result.parts[0])

            # Add tool results as a user message
            messages.append(types.Content(role="user", parts=function_responses))
        else:
            print(response.text)
            break


if __name__ == "__main__":
    main()
