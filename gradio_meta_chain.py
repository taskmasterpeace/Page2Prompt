import asyncio
from typing import Dict, List
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None  # Initialize as None
        self.director_styles = {"Default": {}}  # Add more styles as needed

    async def generate_prompt(self, style: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, active_subjects: list = None, full_script: str = "", prompt_type: str = "normal") -> Dict[str, Dict[str, str]]:
        try:
            import logging
            logging.debug(f"MetaChain.generate_prompt called with prompt_type: {prompt_type}")
            
            # Generate prompts for all types
            prompt_types = ["concise", "normal", "detailed"]
            results = {}
            
            for p_type in prompt_types:
                prompt_template = self._get_prompt_template(p_type)
                
                subject_info = self._format_subject_info(active_subjects)
                
                prompt_input = {
                    "style_prefix": style.split('--')[0].strip() if '--' in style else style,
                    "style_suffix": style.split('--')[1].strip() if '--' in style else "",
                    "highlighted_text": highlighted_text,
                    "shot_description": shot_description,
                    "directors_notes": directors_notes,
                    "script": script,
                    "stick_to_script": "Strictly adhere to the provided script." if stick_to_script else "Use the script as inspiration, but feel free to be creative.",
                    "end_parameters": end_parameters,
                    "subject_info": subject_info,
                    "full_script": full_script,
                }
                
                generated_prompt = prompt_template.format(**prompt_input)
                results[p_type] = {"Full Prompt": generated_prompt}
            
            return results
        except Exception as e:
            logging.exception("Error in MetaChain.generate_prompt")
            raise PromptGenerationError(f"Failed to generate prompt: {str(e)}")

    def _get_prompt_template(self, prompt_type: str) -> str:
        base_template = "{style_prefix} {content} {style_suffix} {end_parameters}"
        templates = {
            "concise": base_template.format(content="[Subject] [Action/Pose] in [Context/Setting], [Time of Day], [Weather Conditions], [Composition]"),
            "normal": base_template.format(content="[Subject] [Action/Pose] in [Context/Setting], [Time of Day], [Weather Conditions], [Composition], [Foreground Elements], [Background Elements], [Mood/Atmosphere]"),
            "detailed": base_template.format(content="[Subject] [Action/Pose] in [Context/Setting], [Time of Day], [Weather Conditions], [Composition], [Foreground Elements], [Background Elements], [Mood/Atmosphere], [Props/Objects], [Environmental Effects]")
        }
        return templates.get(prompt_type, templates["normal"])

    def _format_subject_info(self, active_subjects: List[Dict]) -> str:
        if not active_subjects:
            return "No active subjects"
        return ", ".join([f"{s.get('name', '')} ({s.get('category', '')}: {s.get('description', '')})" for s in active_subjects])

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
