import os
from dotenv import load_dotenv
from google import genai



def main():
    print("Hello from ai-agent!")
    load_dotenv()


    api_key =  os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise RuntimeError("Api Key is empty or failed to retrieve")
    else:
        print("API key loaded")
        client = genai.Client(api_key=api_key)
        print("client made")

    content = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
    response = client.models.generate_content(model='gemini-2.5-flash', contents=content)
    
    print(f"User prompt: {content}")
    
    if response.usage_metadata == None:
        raise RuntimeError("response Metadata empty")
    else:
        # number of tokens in the prompt that was sent to the model:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        # number of tokens in the model's response:
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    print("Response:")
    print(response.text)
    


if __name__ == "__main__":
    main()
