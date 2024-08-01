import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key(key_name, prompt_message):
    api_key = os.getenv(key_name)
    if not api_key:
        api_key = input(prompt_message)
        with open(".env", "a") as env_file:
            env_file.write(f"\n{key_name}={api_key}")
    return api_key

# Get the OpenAI API key
OPENAI_API_KEY = get_api_key("OPENAI_API_KEY", "Please enter your OpenAI API key: ")

# Get the LangSmith API key
LANGSMITH_API_KEY = get_api_key("LANGSMITH_API_KEY", "Please enter your LangSmith API key: ")

# Function to get the OpenAI API key
def get_openai_api_key():
    return OPENAI_API_KEY

# Function to get the LangSmith API key
def get_langsmith_api_key():
    return LANGSMITH_API_KEY
