from typing import Dict, List
import json
import os
import logging
import logging
class PromptManager:
    def __init__(self, save_file: str = "saved_prompts.json"):
        self.save_file = save_file
        self.saved_prompts = self._load_prompts()

    def save_prompt(self, prompt: str, style_prefix: str, style_suffix: str, camera_move: str, camera_shot: str, components: Dict):
        self.saved_prompts.append({
            "prompt": prompt,
            "style_prefix": style_prefix,
            "style_suffix": style_suffix,
            "camera_move": camera_move,
            "camera_shot": camera_shot,
            "components": components
        })
        self._save_prompts()

    def load_prompt(self, index: int) -> Dict:
        if 0 <= index < len(self.saved_prompts):
            return self.format_prompt(self.saved_prompts[index])
        else:
            raise IndexError("Prompt index out of range")

    def get_all_prompts(self) -> List[Dict]:
        return [self.format_prompt(prompt) for prompt in self.saved_prompts]

    def delete_prompt(self, index: int):
        if 0 <= index < len(self.saved_prompts):
            del self.saved_prompts[index]
            self._save_prompts()
        else:
            raise IndexError("Prompt index out of range")

    def format_prompt(self, prompt_dict: Dict) -> Dict:
        formatted_prompt = (
            f"{prompt_dict['camera_move']} {prompt_dict['style_prefix']} "
            f"{prompt_dict['camera_shot']} {prompt_dict['prompt']} {prompt_dict['style_suffix']}"
        )
        return {**prompt_dict, "formatted_prompt": formatted_prompt}

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

    def update_prompt(self, index: int, prompt: str, style_prefix: str, style_suffix: str, camera_move: str, camera_shot: str, components: Dict):
        if 0 <= index < len(self.saved_prompts):
            self.saved_prompts[index] = {
                "prompt": prompt,
                "style_prefix": style_prefix,
                "style_suffix": style_suffix,
                "camera_move": camera_move,
                "camera_shot": camera_shot,
                "components": components
            }
            self._save_prompts()
        else:
            raise IndexError("Prompt index out of range")
