import json
import os

class PromptManager:
    def __init__(self, save_file: str = "saved_prompts.json"):
        self.save_file = save_file
        self.prompts = self._load_prompts()

    def save_prompt(self, prompt, name, style, highlighted_text, shot_description, metadata):
        formatted_prompt = self.format_prompt({
            "name": name,
            "prompt": prompt,
            "style": style,
            "highlighted_text": highlighted_text,
            "shot_description": shot_description,
            "metadata": metadata
        })
        self.prompts.append(formatted_prompt)
        self._save_prompts()

    def format_prompt(self, prompt_dict):
        return {
            "name": prompt_dict["name"],
            "formatted_prompt": f"Style: {prompt_dict['style']}\n"
                                f"Highlighted Text: {prompt_dict['highlighted_text']}\n"
                                f"Shot Description: {prompt_dict['shot_description']}\n"
                                f"Prompt: {prompt_dict['prompt']}"
        }

    def get_all_prompts(self):
        return self.prompts

    def _save_prompts(self):
        with open(self.save_file, 'w') as f:
            json.dump(self.prompts, f)

    def _load_prompts(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                return json.load(f)
        return []
