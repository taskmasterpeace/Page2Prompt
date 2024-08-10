import asyncio
from gradio_meta_chain import MetaChain
from gradio_styles import StyleManager
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError

class PromptForgeCore:
    def __init__(self):
        self.meta_chain = MetaChain(self)
        self.style_manager = StyleManager()
        self.prompt_logger = PromptLogger("prompt_log.json")

    async def generate_prompt(self, style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters):
        try:
            result = await self.meta_chain.generate_prompt(
                style=style,
                highlighted_text=highlighted_text,
                shot_description=shot_description,
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                end_parameters=end_parameters
            )
            return result
        except Exception as e:
            raise PromptGenerationError(str(e))

    async def analyze_script(self, script_content, director_style):
        try:
            return await self.meta_chain.analyze_script(script_content, director_style)
        except Exception as e:
            raise ScriptAnalysisError(str(e))

    def get_director_styles(self):
        return list(self.meta_chain.director_styles.keys())
