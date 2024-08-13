import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError
from gradio_config import get_openai_api_key

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None  # Initialize as None
        self.director_styles = {"Default": {}}  # Add more styles as needed

    def _initialize_llm(self, temperature: float = 0.7):
        logger.debug(f"Initializing LLM with temperature {temperature}")
        try:
            from langchain_openai import ChatOpenAI
            from gradio_config import get_openai_api_key
            
            api_key = get_openai_api_key()
            if not api_key:
                raise ValueError("OpenAI API key is not set in the environment or configuration.")
            self.llm = ChatOpenAI(model_name="gpt-4", openai_api_key=api_key)
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize LLM: {str(e)}")
            raise

    async def generate_prompt(self, style: Optional[str], highlighted_text: Optional[str], shot_description: str, directors_notes: str, script: Optional[str], stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", temperature: float = 0.7, camera_shot: Optional[str] = None, camera_move: Optional[str] = None, length: str = "detailed") -> Dict[str, str]:
        logger.info(f"Generating prompt with inputs: style={style}, highlighted_text={highlighted_text[:50] if highlighted_text else 'None'}..., shot_description={shot_description[:50]}..., directors_notes={directors_notes[:50]}..., script={script[:50] if script else 'None'}..., stick_to_script={stick_to_script}, end_parameters={end_parameters}, active_subjects={active_subjects}, full_script={full_script[:50]}..., temperature={temperature}, camera_shot={camera_shot}, camera_move={camera_move}, length={length}")
        
        # Map the length parameter to word counts
        length_to_words = {
            "concise": "about 20 words",
            "normal": "about 50 words",
            "detailed": "about 100 words"
        }
        word_count = length_to_words.get(length, "about 100 words")  # Default to detailed if invalid length is provided
    
        # Use default values for empty inputs
        style = style or "Default style"
        highlighted_text = highlighted_text or "Default scene"
        script = script or full_script or "Default script"
        shot_description = shot_description or "Default shot"
        directors_notes = directors_notes or "No specific notes"
        camera_shot = camera_shot or ""
        camera_move = camera_move or ""

        try:
            self._initialize_llm(temperature)
            subject_info = self._format_subject_info(active_subjects)
        
            style_prefix = style.split('--')[0].strip() if '--' in style else style
            style_suffix = style.split('--')[1].strip() if '--' in style else ""
            
            template = self._get_prompt_template(word_count)
            chain = RunnableSequence(template | self.llm)
            
            script_adherence = 'Strictly adhere to the provided script.' if stick_to_script else 'Use the script as inspiration, but feel free to be creative.'
            input_data = {
                "style_prefix": style_prefix,
                "style_suffix": style_suffix,
                "shot_description": shot_description,
                "directors_notes": directors_notes,
                "highlighted_text": highlighted_text,
                "full_script": full_script or script,
                "subject_info": subject_info,
                "end_parameters": end_parameters,
                "script_adherence": script_adherence,
                "camera_shot": camera_shot,
                "camera_move": camera_move,
                "length": length
            }
            logger.debug(f"Invoking chain for detailed prompt with input: {input_data}")
            result = await chain.ainvoke(input_data)
            logger.debug(f"Chain result: {result.content}")
            structured_output = self._structure_prompt_output(result.content)
            
            full_prompt_parts = [
                structured_output.get("Camera Shot", ""),
                structured_output.get("Camera Move", ""),
                style_prefix,
                structured_output['Full Prompt'],
                style_suffix,
                end_parameters
            ]
            full_prompt = " ".join(filter(None, full_prompt_parts)).strip()
            structured_output['Full Prompt'] = full_prompt
            
            logger.info(f"Generated prompt: {structured_output}")
            return structured_output
        except Exception as e:
            error_msg = f"Failed to generate prompt: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}

    def derive_concise_prompt(self, detailed_prompt: str) -> str:
        # Implement logic to derive a concise prompt (about 20 words) from the detailed prompt
        words = detailed_prompt.split()
        return " ".join(words[:20])

    def derive_normal_prompt(self, detailed_prompt: str) -> str:
        # Implement logic to derive a normal prompt (about 50 words) from the detailed prompt
        words = detailed_prompt.split()
        return " ".join(words[:50])

    def _get_prompt_template(self, length: str) -> PromptTemplate:
        base_template = """
        Generate a {length} prompt based on the following information:
        Subjects: {{subject_info}}
        Camera Shot: {{camera_shot}}
        Camera Move: {{camera_move}}
        Style Prefix: {{style_prefix}}
        Style Suffix: {{style_suffix}}
        Shot Description: {{shot_description}}
        Director's Notes: {{directors_notes}}
        Highlighted Script: {{highlighted_text}}
        Full Script: {{full_script}}
        End Parameters: {{end_parameters}}

        {{script_adherence}}

        The prompt should follow this structure:
        [Camera Shot] [Camera Move] [Style Prefix] [Subject] [Action/Pose] in [Context/Setting], [Time of Day], [Weather Conditions], [Composition], [Foreground Elements], [Background Elements], [Mood/Atmosphere], [Props/Objects], [Environmental Effects] [Style Suffix] [End Parameters]

        Important:
        1. Describe the scene positively. Don't use phrases like "no additional props" or "no objects present". Instead, focus on what is in the scene.
        2. Do not include any visual style elements or descriptors (e.g., 3D, comic book style) in the main body of the prompt. These should only be in the Style Prefix or Style Suffix.
        3. If Camera Shot or Camera Move are not provided, do not mention them in the prompt.

        Generate a structured output with the following fields:
        1. Camera Shot
        2. Camera Move
        3. Subject
        4. Action/Pose
        5. Context/Setting
        6. Time of Day
        7. Weather Conditions
        8. Composition
        9. Foreground Elements
        10. Background Elements
        11. Mood/Atmosphere
        12. Props/Objects
        13. Environmental Effects
        14. Full Prompt

        Prompt:
        """

        return PromptTemplate(
            input_variables=["style_prefix", "style_suffix", "shot_description", "directors_notes", "highlighted_text", "full_script", "subject_info", "end_parameters", "script_adherence", "camera_shot", "camera_move", "length"],
            template=base_template
        )

    def _format_subject_info(self, active_subjects: Optional[List[Dict]]) -> str:
        if not active_subjects:
            return "No active subjects"
        return ", ".join([f"{s.get('name', '')} ({s.get('category', '')}: {s.get('description', '')})" for s in active_subjects if isinstance(s, dict)])

    def _structure_prompt_output(self, content: str) -> Dict[str, str]:
        try:
            lines = content.strip().split('\n')
            structured_output = {
                "Camera Shot": "", "Camera Move": "", "Subject": "", "Action/Pose": "",
                "Context/Setting": "", "Time of Day": "", "Weather Conditions": "",
                "Composition": "", "Foreground Elements": "", "Background Elements": "",
                "Mood/Atmosphere": "", "Props/Objects": "", "Environmental Effects": "",
                "Full Prompt": ""
            }
            current_field = ""
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in structured_output:
                        current_field = key
                        structured_output[current_field] = value
                elif current_field:
                    structured_output[current_field] += " " + line.strip()
            
            # If 'Full Prompt' is empty, construct it from other fields
            if not structured_output["Full Prompt"]:
                full_prompt_parts = []
                for key, value in structured_output.items():
                    if key != "Full Prompt" and value:
                        if key in ["Camera Shot", "Camera Move"]:
                            full_prompt_parts.insert(0, value)
                        else:
                            full_prompt_parts.append(value)
                structured_output["Full Prompt"] = " ".join(full_prompt_parts)
            
            # Ensure 'Full Prompt' is not empty
            if not structured_output["Full Prompt"]:
                raise ValueError("Failed to generate a valid prompt")
            
            return structured_output
        except Exception as e:
            logger.error(f"Error in _structure_prompt_output: {str(e)}")
            return {"Full Prompt": f"Error in structuring output: {str(e)}"}

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
