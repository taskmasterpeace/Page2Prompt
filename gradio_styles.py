import json
import os

class StyleManager:
    def __init__(self, filename: str = "styles.json"):
        self.filename = filename
        self.styles = self.load_styles()

    def load_styles(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {"Default": {}}

    def save_styles(self):
        with open(self.filename, 'w') as f:
            json.dump(self.styles, f)

    def get_style_names(self):
        return list(self.styles.keys())

    def get_style(self, name):
        style = self.styles.get(name, {})
        return style.get('prefix', ''), style.get('suffix', '')

    def add_style(self, name, prefix, suffix):
        self.styles[name] = {'prefix': prefix, 'suffix': suffix}
        self.save_styles()

    def add_style(self, name, style_dict):
        self.styles[name] = style_dict
        self.save_styles()

    def remove_style(self, name):
        if name in self.styles:
            del self.styles[name]
            self.save_styles()

    def get_style_prefix(self, name: str) -> str:
        return self.styles.get(name, {}).get('prefix', '')
