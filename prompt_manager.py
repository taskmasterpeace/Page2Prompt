from typing import Dict, List
import json
import os
import logging
import logging
class PromptManager:
    def __init__(self, save_file: str = "saved_prompts.json"):
        self.save_file = save_file
        self.saved_prompts = self._load_prompts()

    def save_prompt(self, prompt: str, components: Dict):
        self.saved_prompts.append({"prompt": prompt, "components": components})
        self._save_prompts()

    def load_prompt(self, index: int) -> Dict:
        if 0 <= index < len(self.saved_prompts):
            return self.saved_prompts[index]
        else:
            raise IndexError("Prompt index out of range")

    def get_all_prompts(self) -> List[Dict]:
        return self.saved_prompts

    def delete_prompt(self, index: int):
        if 0 <= index < len(self.saved_prompts):
            del self.saved_prompts[index]
            self._save_prompts()
        else:
            raise IndexError("Prompt index out of range")

    def _save_prompts(self):
        with open(self.save_file, 'w') as f:
            json.dump(self.saved_prompts, f)

    def _load_prompts(self) -> List[Dict]:
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    content = f.read()
                    if content.strip():  # Check if file is not empty
                        return json.loads(content)
                    else:
                        logging.warning(f"The file {self.save_file} is empty.")
                        return []
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {self.save_file}: {e}")
                return []
        else:
            logging.info(f"The file {self.save_file} does not exist. Creating a new one.")
            with open(self.save_file, 'w') as f:
                json.dump([], f)
            return []

    def search_prompts(self, keyword: str) -> List[Dict]:
        return [prompt for prompt in self.saved_prompts 
                if keyword.lower() in prompt['prompt'].lower() 
                or any(keyword.lower() in str(v).lower() for v in prompt['components'].values())]

    def update_prompt(self, index: int, prompt: str, components: Dict):
        if 0 <= index < len(self.saved_prompts):
            self.saved_prompts[index] = {"prompt": prompt, "components": components}
            self._save_prompts()
        else:
            raise IndexError("Prompt index out of range")
