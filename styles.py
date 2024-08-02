import json
from typing import List, Dict

class StyleManager:
    def __init__(self, filename: str = "styles.json"):
        self.filename = filename
        self.styles = self.load_styles()

    def load_styles(self) -> Dict[str, Dict[str, str]]:
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_styles(self):
        with open(self.filename, 'w') as f:
            json.dump(self.styles, f, indent=2)

    def add_style(self, name: str, prefix: str, suffix: str):
        self.styles[name] = {"prefix": prefix, "suffix": suffix}
        self.save_styles()

    def get_style(self, name: str) -> Dict[str, str]:
        return self.styles.get(name, {"prefix": "", "suffix": ""})

    def get_style_names(self) -> List[str]:
        return list(self.styles.keys())

    def remove_style(self, name: str):
        if name in self.styles:
            del self.styles[name]
            self.save_styles()

predefined_styles = {
    "Classic Comic Book": {
        "prefix": "In the style of a classic comic book,",
        "suffix": "with bold outlines, vibrant colors, and dynamic action poses"
    },
    "Pixar Disney": {
        "prefix": "In the style of a Pixar Disney animation,",
        "suffix": "with expressive characters, detailed textures, and warm lighting"
    },
    # Add more predefined styles here
}
