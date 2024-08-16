import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError
from gradio_config import get_openai_api_key

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import time

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None
        self.director_styles = {"Default": {}}  # Add more styles as needed
        self.initialize_llm()

    def initialize_llm(self, temperature: float = 0.7):
        logger.debug(f"Initializing LLM with temperature {temperature}")
        try:
            from langchain_openai import ChatOpenAI
            from gradio_config import get_openai_api_key
            
            api_key = get_openai_api_key()
            if not api_key:
                raise ValueError("OpenAI API key is not set in the environment or configuration.")
            self.llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=api_key, temperature=temperature)
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize LLM: {str(e)}")
            raise

    async def generate_prompt(self, style: Optional[str], highlighted_text: Optional[str], shot_description: str, directors_notes: str, script: Optional[str], stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", camera_shot: Optional[str] = None, camera_move: Optional[str] = None, camera_size: Optional[str] = None, length: str = "detailed") -> Dict[str, str]:
        start_time = time.time()
        logger.info(f"Generating prompt with inputs: style={style}, highlighted_text={highlighted_text[:50] if highlighted_text else 'None'}..., shot_description={shot_description[:50]}..., directors_notes={directors_notes[:50]}..., script={script[:50] if script else 'None'}..., stick_to_script={stick_to_script}, end_parameters={end_parameters}, active_subjects={active_subjects}, full_script={full_script[:50]}..., camera_shot={camera_shot}, camera_move={camera_move}, length={length}")
        
        # Map the length parameter to word counts
        length_to_words = {
            "concise": "about 20 words",
            "normal": "about 50 words",
            "detailed": "about 100 words"
        }
        word_count = length_to_words.get(length, "about 100 words")  # Default to detailed if invalid length is provided
    
        # Use default values for empty inputs
        highlighted_text = highlighted_text or "Default scene"
        script = script or full_script or "Default script"
        shot_description = shot_description or "Default shot"
        directors_notes = directors_notes or "No specific notes"

        try:
            script_analysis_start = time.time()
            subject_info = self._format_subject_info(active_subjects)
            logger.info(f"Script analysis took {time.time() - script_analysis_start:.2f} seconds")
        
            prompt_generation_start = time.time()
            
            template = self._get_prompt_template(word_count)
            chain = RunnableSequence(template | self.llm)
            
            script_adherence = 'Strictly adhere to the provided script.' if stick_to_script else 'Use the script as inspiration, but feel free to be creative.'
            subject_info = self._format_subject_info(active_subjects)
        
            input_data = {
                "style": style,
                "style_prefix": self.core.style_manager.get_style_prefix(style),
                "shot_description": shot_description,
                "directors_notes": directors_notes,
                "highlighted_text": highlighted_text,
                "full_script": full_script or script,
                "subject_info": subject_info,
                "end_parameters": end_parameters,
                "script_adherence": script_adherence,
                "camera_shot": camera_shot,
                "camera_move": camera_move,
                "camera_size": camera_size,
                "length": length
            }
            logger.debug(f"Input data for prompt generation: {input_data}")
            logger.debug(f"Invoking chain for prompt generation with input: {input_data}")
            result = await chain.ainvoke(input_data)
            logger.debug(f"Chain result: {result.content}")
            
            prompts = self._structure_prompt_output(result.content, input_data)
            
            logger.info(f"Prompt generation took {time.time() - prompt_generation_start:.2f} seconds")
            style_prefix = input_data.get("style_prefix", "")
            style_suffix = input_data.get("end_parameters", "")
            logger.info(f"Generated prompts: {prompts}")
            logger.debug(f"Style Prefix: {style_prefix}, Style Suffix: {style_suffix}")
            logger.debug(f"Formatted Prompts: {prompts}")
            return prompts
        except Exception as e:
            error_msg = f"Failed to generate prompt: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}
        finally:
            logger.info(f"generate_prompt took {time.time() - start_time:.2f} seconds total")

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
        Generate three prompts (concise, normal, and detailed) based on the following information:
        Subjects: {subject_info}
        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Highlighted Script: {highlighted_text}
        Full Script: {full_script}
        End Parameters: {end_parameters}
        Style: {style}
        Style Prefix: {style_prefix}

        {script_adherence}

        Important:
        1. Incorporate the camera work description seamlessly into the scene description. The camera work is already included at the beginning of the Shot Description.
        2. Describe the scene positively. Don't use phrases like "no additional props" or "no objects present". Instead, focus on what is in the scene.
        3. Only include camera information if it's provided in the input.
        4. Never include style information in the image prompt. That is done in the Style and Style Prefix Only.
        5. Generate three separate paragraphs: concise (about 20 words), normal (about 50 words), and detailed (about 100 words). Separate them by a space. Do not add headings for these.
        6. Consider the main subject and its placement. Think about depth. Include elements in the foreground, middle ground, and background to create a sense of dimension when the shot requires it; do not force it.

        Prompts:
        """

        return PromptTemplate(
            input_variables=["style", "style_prefix", "shot_description", "directors_notes", "highlighted_text", "full_script", "subject_info", "end_parameters", "script_adherence", "camera_shot", "camera_move", "camera_size", "length"],
            template=base_template
        )

    def _format_subject_info(self, active_subjects: Optional[List[Dict]]) -> str:
        if not active_subjects:
            return "No active subjects"
        return ", ".join([f"{s.get('name', '')} ({s.get('category', '')}: {s.get('description', '')})" for s in active_subjects if isinstance(s, dict)])

    def _structure_prompt_output(self, content: str, input_data: Dict[str, Any]) -> Dict[str, str]:
        try:
            paragraphs = content.strip().split('\n\n')
            if len(paragraphs) != 3:
                raise ValueError("Expected 3 paragraphs in the output")
            
            style_prefix = input_data.get("style_prefix", "")
            style_suffix = input_data.get("end_parameters", "")

            prompts = {
                "Concise Prompt": f"{style_prefix} {paragraphs[0].strip()} {style_suffix}".strip(),
                "Normal Prompt": f"{style_prefix} {paragraphs[1].strip()} {style_suffix}".strip(),
                "Detailed Prompt": f"{style_prefix} {paragraphs[2].strip()} {style_suffix}".strip()
            }
            logger.debug(f"Formatted Prompts with Prefix and Suffix: {prompts}")
            
            return prompts
        except Exception as e:
            logger.error(f"Error in _structure_prompt_output: {str(e)}")
            return {"error": f"Error in structuring output: {str(e)}", "Full Prompt": content.strip()}

    async def generate_style_suffix(self, style_prefix: str) -> str:
        try:
            template = PromptTemplate(
                input_variables=["style_prefix"],
                template="Based on the style prefix '{style_prefix}', write 5 distinct visual descriptions characteristics of the style prefix. Write the words out seperated by semi colons Like this. X;X;X;X;X  Each characteristic should be a single word followed by a colon. Focus only on visual aspects, not story-related elements."
            )
            chain = RunnableSequence(template | self.llm)
            result = await chain.ainvoke({"style_prefix": style_prefix})
            return result.content.strip()
        except Exception as e:
            logger.error(f"Error in generate_style_suffix: {str(e)}")
            return f"Error generating style suffix: {str(e)}"

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
