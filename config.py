import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# If the API key is not set, prompt the user to enter it
if not API_KEY:
    API_KEY = input("Please enter your OpenAI API key: ")
    
    # Save the API key to a .env file
    with open(".env", "w") as env_file:
        env_file.write(f"OPENAI_API_KEY={API_KEY}")

# Function to get the API key
def get_api_key():
    return API_KEY
