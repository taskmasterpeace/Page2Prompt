import asyncio
import json
import logging
import time
import re
from typing import Dict, List, Optional, Union, Any
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError
from gradio_config import get_openai_api_key
from pydantic import BaseModel
from gradio_core import save_debug_output

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_json_string(json_string: str) -> str:
    """
    Remove markdown formatting and clean the JSON string.
    """
    # Remove markdown code block indicators
    json_string = re.sub(r'^```json\s*', '', json_string, flags=re.MULTILINE)
    json_string = re.sub(r'\s*```$', '', json_string, flags=re.MULTILINE)
    
    # Remove any leading/trailing whitespace
    json_string = json_string.strip()
    
    # Handle potential YAML-style start of the document
    json_string = re.sub(r'^---\s*', '', json_string)
    
    return json_string

class Shot(BaseModel):
    scene_number: int
    shot_number: int
    script_content: str
    shot_description: str
    characters: List[str]
    camera_work: str
    shot_type: str
    completed: bool = False

class ShotList(BaseModel):
    shots: List[Shot]

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None
        self.director_styles = {"Default": {}}  # Add more styles as needed
        self.initialize_llm()
        self.load_director_styles()

    def load_director_styles(self):
        self.director_styles.update({
            "Alfred Hitchcock": {
                "camera_angles": ["Dutch angle", "High angle", "Low angle"],
                "lighting": "High contrast lighting with deep shadows",
                "pacing": "Slow build-up with sudden bursts of tension",
                "color_palette": "Muted colors with occasional bold accents",
                "composition": "Off-center framing, use of foreground objects for depth",
                "motifs": "Staircases, birds, blonde women",
                "typical_shots": "Dolly zoom, point-of-view shots"
            },
            "Wes Anderson": {
                "camera_angles": ["Symmetrical framing", "Center composition"],
                "lighting": "Soft, warm lighting with pastel hues",
                "pacing": "Deliberate and methodical with quirky interludes",
                "color_palette": "Pastel colors with pops of vibrant hues",
                "composition": "Symmetrical compositions, flat space",
                "motifs": "Dysfunctional families, vintage aesthetics",
                "typical_shots": "Overhead shots, slow-motion walking scenes"
            },
            "Christopher Nolan": {
                "camera_angles": ["IMAX-friendly compositions", "Wide shots"],
                "lighting": "Natural, high-contrast lighting",
                "pacing": "Non-linear, intercut storylines",
                "color_palette": "Cool tones with occasional warm accents",
                "composition": "Practical effects, minimal CGI",
                "motifs": "Time manipulation, moral ambiguity",
                "typical_shots": "Rotating sets, practical stunts"
            },
            "Quentin Tarantino": {
                "camera_angles": ["Low angle shots", "Trunk shots"],
                "lighting": "Vibrant, stylized lighting",
                "pacing": "Non-linear narrative with chapter-like structure",
                "color_palette": "Bold, saturated colors",
                "composition": "Close-ups of objects, feet",
                "motifs": "Pop culture references, violence",
                "typical_shots": "Long takes, Mexican standoffs"
            },
            "Stanley Kubrick": {
                "camera_angles": ["One-point perspective", "Slow zoom"],
                "lighting": "Natural light and practical sources",
                "pacing": "Slow, deliberate with moments of intensity",
                "color_palette": "Bold use of single colors in scenes",
                "composition": "Symmetrical, geometric compositions",
                "motifs": "Dehumanization, social commentary",
                "typical_shots": "Steadicam tracking shots, extreme wide shots"
            }
        })

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

    async def generate_prompt(self, style: Optional[str], highlighted_text: Optional[str], shot_description: str, directors_notes: str, script: Optional[str], stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", camera_shot: Optional[str] = None, camera_move: Optional[str] = None, camera_size: Optional[str] = None, length: str = "detailed", director_style: Optional[str] = None) -> Dict[str, str]:
        start_time = time.time()
        logger.info(f"Generating prompt with inputs: style={style}, highlighted_text={highlighted_text[:50] if highlighted_text else 'None'}..., shot_description={shot_description[:50]}..., directors_notes={directors_notes[:50]}..., script={script[:50] if script else 'None'}..., stick_to_script={stick_to_script}, end_parameters={end_parameters}, active_subjects={active_subjects}, full_script={full_script[:50]}..., camera_shot={camera_shot}, camera_move={camera_move}, length={length}, director_style={director_style}")
        
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
        director_style = director_style or "Default"

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
                "length": length,
                "director_style": director_style
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
        except KeyError as e:
            error_msg = f"Missing input variable: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in generate_prompt: {str(e)}"
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
        Director's Style: {director_style}
        Camera Shot: {camera_shot}
        Camera Move: {camera_move}
        Camera Size: {camera_size}
        Length: {length}

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
            input_variables=[
                "style", "style_prefix", "shot_description", "directors_notes",
                "highlighted_text", "full_script", "subject_info", "end_parameters",
                "script_adherence", "camera_shot", "camera_move", "camera_size",
                "length", "director_style"
            ],
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
                template="Based on the style prefix '{style_prefix}', generate 5 distinct visual characteristics of this style. Each characteristic should be a single word or short phrase. Separate them with semicolons. Focus only on visual aspects, not story-related elements. Format: characteristic1;characteristic2;characteristic3;characteristic4;characteristic5"
            )
            chain = RunnableSequence(template | self.llm)
            result = await chain.ainvoke({"style_prefix": style_prefix})
            return result.content.strip()
        except Exception as e:
            logger.error(f"Error in generate_style_suffix: {str(e)}")
            return f"Error generating style suffix: {str(e)}"

    from pydantic import BaseModel
    from typing import List, Optional, Dict, Any
    import json
    import json
    from pydantic import BaseModel

    class Shot(BaseModel):
        scene_number: int
        shot_number: int
        script_content: str
        shot_description: str
        characters: List[str]
        camera_work: str
        shot_type: str
        completed: bool = False

    class ShotList(BaseModel):
        shots: List[Shot]

    async def analyze_script(self, script: str, director_style: str) -> Dict[str, Any]:
        try:
            template = PromptTemplate(
                input_variables=["script", "director_style"],
                template="""
                As an expert prompt engineer and cinematographer, analyze the following script using the directorial style of {director_style}. 
                Generate a comprehensive shot list that aligns with the Page2Prompt application's functionality and the director's unique approach.

                For each significant moment or scene, provide:

                1. Scene Number: Numerical identifier for the scene.
                2. Shot Number: Numerical identifier for the shot within the scene.
                3. Script Content: The exact portion of the script this shot is based on.
                4. Shot Description: Concise description of the visual elements, considering the director's style. Include actions, setting, and any important details.
                5. Characters: Main characters present in the shot (as a comma-separated list).
                6. Camera Work: Specify the shot type, camera movement, and any special techniques typical of the director.
                7. Shot Type: Specify if it's an establishing shot, insert, close-up, etc.

                Ensure that the shot list reflects {director_style}'s signature elements such as composition, lighting, pacing, color palette, recurring motifs, and typical shot choices.

                Provide the output in the following JSON format:
                {{
                    "shots": [
                        {{
                            "scene_number": 1,
                            "shot_number": 1,
                            "script_content": "Exact portion of the script for this shot",
                            "shot_description": "Detailed description of the shot",
                            "characters": ["Character1", "Character2"],
                            "camera_work": "Description of camera work",
                            "shot_type": "Establishing shot/Insert/Close-up/etc.",
                            "completed": false
                        }},
                        // ... more shots ...
                    ]
                }}

                Script:
                {script}

                Shot List:
                """
            )
        
            chain = RunnableSequence(template | self.llm)
            result = await chain.ainvoke({"script": script, "director_style": director_style})
        
            # Save raw output for debugging
            save_debug_output(result.content, f"raw_llm_output_{int(time.time())}.txt")
        
            # Log the raw content and its type
            logger.debug(f"Result type: {type(result.content)}, content: {result.content}")
        
            # Check if content is empty
            if not result.content.strip():
                raise ValueError("Received empty content from LLM")
        
            # Clean the JSON string
            cleaned_content = clean_json_string(result.content)
            
            # Attempt to parse the JSON
            try:
                if isinstance(cleaned_content, list):
                    shot_list_dict = {"shots": cleaned_content}
                else:
                    shot_list_dict = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Problematic content: {cleaned_content}")
                raise ScriptAnalysisError(f"Failed to parse JSON: {str(e)}")
            except TypeError as e:
                logger.error(f"Type error: {str(e)}")
                logger.error(f"Problematic content type: {type(cleaned_content)}")
                raise ScriptAnalysisError(f"Unexpected data type: {str(e)}")
        
            # Validate the structure of the parsed JSON
            if not isinstance(shot_list_dict, dict) or 'shots' not in shot_list_dict:
                raise ValueError("Parsed JSON does not have the expected structure")
        
            # Convert the shot list to the required format
            shot_list = []
            for shot in shot_list_dict['shots']:
                shot_list.append({
                    'Scene': shot.get('scene_number', ''),
                    'Shot': shot.get('shot_number', ''),
                    'Script Content': shot.get('script_content', ''),
                    'Shot Description': shot.get('shot_description', ''),
                    'Characters': ', '.join(shot.get('characters', [])),
                    'Camera Work': shot.get('camera_work', ''),
                    'Shot Type': shot.get('shot_type', ''),
                    'Completed': shot.get('completed', False)
                })

            return shot_list

        except ValueError as e:
            logger.exception(f"Value error in analyze_script: {str(e)}")
            raise ScriptAnalysisError(str(e))
        except Exception as e:
            logger.exception(f"Unexpected error in analyze_script: {str(e)}")
            raise ScriptAnalysisError(str(e))

    def _merge_shot_lists(self, ai_shots, core_shots):
        # Merge and deduplicate shots from both sources
        merged_shots = ai_shots + core_shots
        seen = set()
        unique_shots = []
        for shot in merged_shots:
            key = (shot['scene_number'], shot['shot_number'])
            if key not in seen:
                seen.add(key)
                unique_shots.append(shot)
        return sorted(unique_shots, key=lambda x: (x['scene_number'], x['shot_number']))

    def _parse_shot_list(self, content: str) -> Dict[str, Any]:
        lines = content.split('\n')
        shot_list = {
            "suggested_style": "",
            "style_prefix": "",
            "style_suffix": "",
            "shots": []
        }
        current_shot = {}
        current_scene = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("Suggested Style:"):
                shot_list["suggested_style"] = line.split(":", 1)[1].strip()
            elif line.startswith("Style Prefix:"):
                shot_list["style_prefix"] = line.split(":", 1)[1].strip()
            elif line.startswith("Style Suffix:"):
                shot_list["style_suffix"] = line.split(":", 1)[1].strip()
            elif line.startswith("Scene"):
                current_scene = line
            elif line.startswith("Scene Number:"):
                if current_shot:
                    shot_list["shots"].append(current_shot)
                current_shot = {"scene_number": line.split(":", 1)[1].strip()}
            elif line.startswith("Shot Number:"):
                current_shot["shot_number"] = line.split(":", 1)[1].strip()
            elif line.startswith("Shot Description:"):
                current_shot["shot_description"] = line.split(":", 1)[1].strip()
            elif line.startswith("Characters:"):
                current_shot["characters"] = line.split(":", 1)[1].strip()
            elif line.startswith("Camera Work:"):
                current_shot["camera_work"] = line.split(":", 1)[1].strip()
            elif line.startswith("Completed:"):
                current_shot["completed"] = line.split(":", 1)[1].strip().lower() == "true"
            elif current_scene and not line.startswith(("Scene Number:", "Shot Number:", "Shot Description:", "Characters:", "Camera Work:", "Completed:")):
                current_shot["scene_description"] = current_scene
        
        if current_shot:
            shot_list["shots"].append(current_shot)
        
        return shot_list
