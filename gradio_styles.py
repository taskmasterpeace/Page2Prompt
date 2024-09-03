import csv
import os

class StyleManager:
    def __init__(self, filename: str = "styles.csv"):
        self.filename = filename
        self.styles = self.load_styles()

    def load_styles(self):
        styles = {}
        if os.path.exists(self.filename):
            with open(self.filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    styles[row['style_name']] = {'prefix': row['prefix'], 'suffix': row['suffix']}
        if not styles:
            styles["Default"] = {'prefix': '', 'suffix': ''}
        return styles

    def save_styles(self):
        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['style_name', 'prefix', 'suffix'])
            writer.writeheader()
            for name, style in self.styles.items():
                writer.writerow({'style_name': name, 'prefix': style['prefix'], 'suffix': style['suffix']})

    def get_style_names(self):
        return list(self.styles.keys())

    def get_style(self, name):
        return self.styles.get(name, {'prefix': '', 'suffix': ''})

    def add_style(self, name, prefix, suffix):
        self.styles[name] = {'prefix': prefix, 'suffix': suffix}
        self.save_styles()

    def remove_style(self, name):
        if name in self.styles:
            del self.styles[name]
            self.save_styles()

    def get_style_prefix(self, name: str) -> str:
        return self.styles.get(name, {}).get('prefix', '')
