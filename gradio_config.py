import configparser
import os
import requests
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()

    def create_default_config(self):
        self.config['API_KEYS'] = {
            'openai_api_key': '',
            'langsmith_api_key': ''
        }
        self.config['UI_SETTINGS'] = {
            'main_window_geometry': '1200x800',
            'input_frame_height': '400',
            'output_frame_height': '300',
            'main_paned_sash': '866',
            'right_paned_sash1': '476',
            'right_paned_sash2': '795',
            'right_paned_sash': '554'
        }
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get(self, section, key):
        if section == 'API_KEYS' and key == 'openai_api_key':
            return os.environ.get('OPENAI_API_KEY') or self.config.get(section, key)
        return self.config.get(section, key)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save_config()

def get_openai_api_key():
    return os.environ.get('OPENAI_API_KEY') or Config().get('API_KEYS', 'openai_api_key')

def check_openai_api_key():
    api_key = get_openai_api_key()
    if not api_key:
        logger.error("OpenAI API key is not set")
        return "API key is NOT set"
    return "API key is set"

def check_network_connectivity():
    try:
        response = requests.get('https://api.openai.com/v1/models', 
                                headers={'Authorization': f'Bearer {get_openai_api_key()}'})
        if response.status_code == 200:
            logger.info("Successfully connected to OpenAI API")
            return "Connected successfully"
        else:
            logger.error(f"Failed to connect to OpenAI API. Status code: {response.status_code}")
            return f"Failed to connect, status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.exception(f"Network error when connecting to OpenAI API: {str(e)}")
        return f"Network error: {str(e)}"
