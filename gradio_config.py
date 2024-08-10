import configparser
import os

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
        self.config['DEFAULT'] = {
            'OpenAI_API_Key': '',
            'UI_Settings': {
                'main_window_geometry': '800x600'
            }
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

def get_openai_api_key():
    config = Config()
    return config.get('DEFAULT', 'OpenAI_API_Key')
