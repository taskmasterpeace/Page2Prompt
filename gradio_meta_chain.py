import asyncio
from typing import Dict, List
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None  # Initialize as None
        self.director_styles = {"Default": {}}  # Add more styles as needed

    async def generate_prompt(self, style: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, active_subjects: list = None) -> Dict[str, Dict[str, str]]:
        try:
            return await self.core.generate_prompt(
                active_subjects=active_subjects,
                style=style,
                shot_description=shot_description,
                directors_notes=directors_notes,
                highlighted_text=highlighted_text,
                full_script=script,
                end_parameters=end_parameters,
                stick_to_script=stick_to_script
            )
        except Exception as e:
            raise PromptGenerationError(str(e))

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
