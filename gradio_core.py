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

    async def generate_prompt(self, style: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str) -> Dict[str, str]:
        try:
            style_prefix, style_suffix = self.format_style(style, end_parameters)
            
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
                    stick_to_script=stick_to_script
                )
                prompts[prompt_type] = result

            self.prompt_logger.log_prompt(prompts)
            return prompts
        except Exception as e:
            raise PromptGenerationError(str(e))

    def format_style(self, style: str, end_parameters: str) -> tuple[str, str]:
        # TODO: Implement logic to format style prefix and suffix
        style_prefix = f"{style} "
        style_suffix = f" {end_parameters}"
        return style_prefix, style_suffix

    async def analyze_script(self, script_content, director_style):
        try:
            return await self.meta_chain.analyze_script(script_content, director_style)
        except Exception as e:
            raise ScriptAnalysisError(str(e))

    def get_director_styles(self):
        return list(self.meta_chain.director_styles.keys())
