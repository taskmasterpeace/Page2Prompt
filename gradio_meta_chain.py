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
            
            # Directly generate the prompt here instead of calling self.core.generate_prompt
            prompt_template = self._get_prompt_template(prompt_type)
            
            prompt_input = {
                "style": style,
                "highlighted_text": highlighted_text,
                "shot_description": shot_description,
                "directors_notes": directors_notes,
                "script": script,
                "stick_to_script": stick_to_script,
                "end_parameters": end_parameters,
                "active_subjects": self._format_subject_info(active_subjects),
                "full_script": full_script,
            }
            
            generated_prompt = prompt_template.format(**prompt_input)
            
            return {prompt_type: {"Full Prompt": generated_prompt}}
        except Exception as e:
            logging.exception("Error in MetaChain.generate_prompt")
            raise PromptGenerationError(f"Failed to generate prompt: {str(e)}")

    def _get_prompt_template(self, prompt_type: str) -> str:
        templates = {
            "concise": "Concise ({style}): {shot_description}. {highlighted_text} {end_parameters}",
            "normal": "Normal ({style}): {shot_description}. {highlighted_text}. {directors_notes} {end_parameters}",
            "detailed": "Detailed ({style}): {shot_description}. {highlighted_text}. {directors_notes}. Script: {script} {end_parameters}"
        }
        return templates.get(prompt_type, templates["normal"])

    def _format_subject_info(self, active_subjects: List[Dict]) -> str:
        if not active_subjects:
            return "No active subjects"
        return ", ".join([f"{s['name']} ({s['category']})" for s in active_subjects])

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
