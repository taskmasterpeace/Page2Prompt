import asyncio
from typing import Dict, List, Any, Optional
from gradio_config import Config
from gradio_styles import StyleManager
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError
from gradio_subject_manager import SubjectManager

import logging
import re

logger = logging.getLogger(__name__)

class PromptForgeCore:
    def __init__(self):
        self.config = Config()
        self.meta_chain = None  # We'll set this later
        self.style_manager = StyleManager()
        self.prompt_logger = PromptLogger("prompt_log.json")
        self.subject_manager = SubjectManager()

    def set_meta_chain(self, meta_chain):
        self.meta_chain = meta_chain

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
        shot_list = []
        style_info = self.meta_chain.director_styles.get(director_style, {})
        
        for scene_num, scene in enumerate(scenes, 1):
            scene_characters = [char for char in characters if char in scene["content"]]
            scene_shots = self._generate_scene_shots(scene_num, scene_characters, style_info)
            shot_list.extend(scene_shots)
        
        return shot_list

    def _generate_scene_shots(self, scene_num, characters, style_info):
        shots = [
            {
                "scene_number": scene_num,
                "shot_number": 1,
                "shot_description": f"Establishing shot: {style_info.get('composition', 'Standard composition')}",
                "characters": ', '.join(characters),
                "camera_work": f"{style_info.get('camera_angles', ['Wide shot'])[0]}, {style_info.get('lighting', 'Standard lighting')}",
                "completed": False
            },
            {
                "scene_number": scene_num,
                "shot_number": 2,
                "shot_description": f"Character interaction: Focus on {', '.join(characters[:2])}",
                "characters": ', '.join(characters[:2]),
                "camera_work": f"{style_info.get('camera_angles', ['Medium shot'])[1] if len(style_info.get('camera_angles', [])) > 1 else 'Medium shot'}, {style_info.get('typical_shots', ['Standard shot'])[0]}",
                "completed": False
            },
            {
                "scene_number": scene_num,
                "shot_number": 3,
                "shot_description": f"Detail shot: Emphasize {style_info.get('motifs', ['key elements'])[0]}",
                "characters": "N/A",
                "camera_work": f"{style_info.get('camera_angles', ['Close-up'])[2] if len(style_info.get('camera_angles', [])) > 2 else 'Close-up'}, {style_info.get('pacing', 'Standard pacing')}",
                "completed": False
            }
        ]
        return shots

    def _get_camera_work(self, director_style):
        style_info = self.meta_chain.director_styles.get(director_style, {})
        return f"{style_info.get('typical_shots', ['Standard shot'])[0]}, {style_info.get('lighting', 'Standard lighting')}, {style_info.get('pacing', 'Standard pacing')}"

    def get_director_styles(self):
        return list(self.meta_chain.director_styles.keys())
