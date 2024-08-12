import asyncio
from gradio_meta_chain import MetaChain
from gradio_styles import StyleManager
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError
from typing import Dict, List

class PromptForgeCore:
    def __init__(self):
        self.meta_chain = MetaChain(self)
        self.style_manager = StyleManager()
        self.prompt_logger = PromptLogger("prompt_log.json")

    async def generate_prompt(self, style_prefix: str, style_suffix: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, active_subjects: List[Dict[str, Any]] = None) -> Dict[str, str]:
        try:
            prompts = {}
            for prompt_type in ["concise", "normal", "detailed"]:
                result = await self.meta_chain.generate_prompt(
                    style_prefix=style_prefix,
                    style_suffix=style_suffix,
                    prompt_type=prompt_type,
                    highlighted_text=highlighted_text,
                    shot_description=shot_description,
                    directors_notes=directors_notes,
                    script=script,
                    stick_to_script=stick_to_script,
                    active_subjects=active_subjects
                )
                prompts[prompt_type] = self.format_prompt(result, style_prefix, style_suffix, end_parameters)

            self.prompt_logger.log_prompt(prompts)
            return prompts
        except Exception as e:
            raise PromptGenerationError(str(e))

    def format_prompt(self, prompt: str, style_prefix: str, style_suffix: str, end_parameters: str) -> str:
        return f"{style_prefix} {prompt} {style_suffix} {end_parameters}"

    async def analyze_script(self, script_content, director_style):
        try:
            return await self.meta_chain.analyze_script(script_content, director_style)
        except Exception as e:
            raise ScriptAnalysisError(str(e))

    def get_director_styles(self):
        return list(self.meta_chain.director_styles.keys())
