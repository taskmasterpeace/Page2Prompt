import asyncio
from typing import Dict, List, Any, Optional
from gradio_config import Config
from gradio_styles import StyleManager
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError

# Import MetaChain at the end to avoid circular import
from gradio_meta_chain import MetaChain

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
            # Perform initial analysis
            initial_analysis = await self.meta_chain.analyze_script(script_content, director_style)
            
            # Extract key elements
            scenes = self._extract_scenes(script_content)
            characters = self._extract_characters(script_content)
            
            # Generate detailed shot list
            shot_list = self._generate_shot_list(scenes, characters, director_style)
            
            return {
                "initial_analysis": initial_analysis,
                "scenes": scenes,
                "characters": characters,
                "shot_list": shot_list
            }
        except Exception as e:
            logger.exception("Error in script analysis")
            raise ScriptAnalysisError(f"Script analysis failed: {str(e)}")

    def _extract_scenes(self, script_content):
        # Implement scene extraction logic
        # This is a placeholder implementation
        scenes = script_content.split("\n\n")
        return [{"scene_number": i+1, "content": scene} for i, scene in enumerate(scenes)]

    def _extract_characters(self, script_content):
        # Implement character extraction logic
        # This is a placeholder implementation
        characters = set(re.findall(r'^(\w+):', script_content, re.MULTILINE))
        return list(characters)

    def _generate_shot_list(self, scenes, characters, director_style):
        # Implement shot list generation logic
        # This is a placeholder implementation
        shot_list = []
        for scene in scenes:
            shot_list.append({
                "scene_number": scene["scene_number"],
                "shot_description": f"Wide shot of the scene",
                "characters": [char for char in characters if char in scene["content"]],
                "camera_work": self._get_camera_work(director_style)
            })
        return shot_list

    def _get_camera_work(self, director_style):
        # Implement logic to determine camera work based on director's style
        # This is a placeholder implementation
        camera_works = {
            "Alfred Hitchcock": "Slow, suspenseful tracking shot",
            "Wes Anderson": "Symmetrical, static wide shot",
            "Christopher Nolan": "Dynamic, IMAX-friendly composition",
            "Quentin Tarantino": "Long take with multiple character interactions",
            "Stanley Kubrick": "Slow zoom with one-point perspective"
        }
        return camera_works.get(director_style, "Standard shot composition")

    def get_director_styles(self):
        return list(self.meta_chain.director_styles.keys())
