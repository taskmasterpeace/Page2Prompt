import asyncio
from gradio_meta_chain import MetaChain
from gradio_styles import StyleManager
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError
from gradio_config import Config
from typing import Dict, List, Any, Optional

class PromptForgeCore:
    def __init__(self):
        self.config = Config()
        self.meta_chain = MetaChain(self)
        self.style_manager = StyleManager()
        self.prompt_logger = PromptLogger("prompt_log.json")

    async def generate_prompt(self, style: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", prompt_type: str = "normal", temperature: float = 0.7, camera_shot: str = "", camera_move: str = "") -> Dict[str, str]:
        try:
            result = await self.meta_chain.generate_prompt(
                style=style,
                prompt_type=prompt_type,
                highlighted_text=highlighted_text,
                shot_description=shot_description,
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                active_subjects=active_subjects,
                full_script=full_script,
                end_parameters=end_parameters
            )
            formatted_prompt = self.format_prompt(result, style, end_parameters)
            self.prompt_logger.log_prompt({prompt_type: formatted_prompt})
            return {prompt_type: formatted_prompt}
        except Exception as e:
            raise PromptGenerationError(str(e))

    def format_prompt(self, prompt: str, style: str, end_parameters: str) -> str:
        return f"{style} {prompt} {end_parameters}"

    async def analyze_script(self, script_content, director_style):
        try:
            return await self.meta_chain.analyze_script(script_content, director_style)
        except Exception as e:
            raise ScriptAnalysisError(str(e))

    def get_director_styles(self):
        return list(self.meta_chain.director_styles.keys())
