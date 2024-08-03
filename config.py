import os
import configparser
from cryptography.fernet import Fernet

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.key_file = 'key.key'
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.create_default_config()
        self.config.read(self.config_file)

    def create_default_config(self):
        self.config['API_KEYS'] = {
            'openai_api_key': '',
            'langsmith_api_key': ''
        }
        self.config['UI_SETTINGS'] = {
            'main_window_geometry': '1200x800',
            'input_frame_height': '400',
            'output_frame_height': '300'
        }
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get(self, section, key):
        return self.config.get(section, key)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save_config()

    def get_api_key(self, key_name):
        encrypted_key = self.get('API_KEYS', key_name)
        if encrypted_key:
            return self.decrypt(encrypted_key)
        return None

    def set_api_key(self, key_name, value):
        encrypted_value = self.encrypt(value)
        self.set('API_KEYS', key_name, encrypted_value)

    def encrypt(self, message):
        key = self.load_or_generate_key()
        f = Fernet(key)
        return f.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message):
        key = self.load_or_generate_key()
        f = Fernet(key)
        return f.decrypt(encrypted_message.encode()).decode()

    def load_or_generate_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        return key

config = Config()

def get_openai_api_key():
    return config.get_api_key('openai_api_key')

def get_langsmith_api_key():
    return config.get_api_key('langsmith_api_key')
