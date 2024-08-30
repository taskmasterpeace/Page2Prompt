import json
import os
from typing import Dict, Any

class PromptManager:
    def __init__(self, save_file: str = "saved_prompts.json"):
        self.save_file = save_file
        self.prompts = self._load_prompts()

    def save_prompt(self, prompt: Dict[str, Any], name: str):
        formatted_prompt = self.format_prompt(name, prompt)
        self.prompts.append(formatted_prompt)
        self._save_prompts()

    def format_prompt(self, name: str, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": name,
            "concise_prompt": prompt_dict.get("Concise Prompt", ""),
            "normal_prompt": prompt_dict.get("Normal Prompt", ""),
            "detailed_prompt": prompt_dict.get("Detailed Prompt", "")
        }

    def get_all_prompts(self):
        return self.prompts

    def _save_prompts(self):
        with open(self.save_file, 'w') as f:
            json.dump(self.prompts, f)

    def _load_prompts(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        return []
