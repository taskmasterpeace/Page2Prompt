# core.py

import asyncio
from typing import List, Dict, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI
from meta_chain import MetaChain
import logging
from langchain_core.prompts import PromptTemplate
import json
import os
from openai import AsyncOpenAI
from prompt_log import PromptLogger
from prompt_log import PromptLogger


# Ensure you set your OpenAI API key as an environment variable
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
prompt_logger = PromptLogger()
prompt_logger = PromptLogger()

class Subject:
    CATEGORIES = ["Main Character", "Supporting Character", "Location", "Object"]

    def __init__(self, name: str, category: str, description: str):
        self.name = name
        self.category = category if category in self.CATEGORIES else "Object"
        self.description = description
        self.active = True

    def toggle_active(self) -> None:
        self.active = not self.active

class StyleHandler:
    def __init__(self):
        self.prefix = ""
        self.suffix = ""
        self.llm = ChatOpenAI(temperature=0.7)

    def set_prefix(self, prefix: str) -> None:
        self.prefix = prefix
        self.generate_suffix()

    async def generate_suffix(self) -> None:
        style_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["style"],
                template="Given the style '{style}', generate three distinct visual descriptors that characterize this style. Separate each descriptor with a comma:"
            )
        )
        result = await style_chain.arun({"style": self.prefix})
        self.suffix = result.strip()

    def get_full_style(self) -> str:
        return f"{self.prefix}: {self.suffix}"

class ElementManager:
    def __init__(self):
        self.elements: Dict[str, str] = {
            "subject": "", "action_pose": "", "context_setting": "", "time_of_day": "",
            "weather_conditions": "", "camera_angle": "", "camera_movement": "",
            "lens_type": "", "focal_length": "", "depth_of_field": "", "composition": "",
            "foreground_elements": "", "background_elements": "", "lighting_direction": "",
            "mood_atmosphere": "", "contrast_level": "", "environmental_effects": "",
            "texture_details": "", "props_objects": "", "sound_elements": "", "narrative_moment": ""
        }

    def update_element(self, name: str, value: str) -> None:
        if name in self.elements:
            self.elements[name] = value

    def get_elements(self) -> Dict[str, str]:
        return self.elements

class ScriptParser:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3)

    async def parse_script(self, script: str) -> List[Dict[str, Any]]:
        parse_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["script"],
                template="Parse the following script into scenes. For each scene, identify the setting, characters present, and key actions:\n\n{script}\n\nParsed scenes:"
            )
        )
        result = await parse_chain.arun({"script": script})
        return await self._structure_parsed_scenes(result)

    async def _structure_parsed_scenes(self, parsed_text: str) -> List[Dict[str, Any]]:
        # Implement logic to convert the parsed text into a structured list of scenes
        # This is a placeholder and should be implemented based on the actual output format
        scenes = []
        # Parse the text and populate the scenes list
        return scenes

class SceneAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3)

    async def analyze_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        analyze_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["scene"],
                template="Analyze the following scene and identify key visual elements, mood, and potential camera shots:\n\n{scene}\n\nAnalysis:"
            )
        )
        result = await analyze_chain.arun({"scene": json.dumps(scene)})
        return await self._structure_analysis(result)

    async def _structure_analysis(self, analysis_text: str) -> Dict[str, Any]:
        # Implement logic to convert the analysis text into a structured dictionary
        # This is a placeholder and should be implemented based on the actual output format
        analysis = {}
        # Parse the text and populate the analysis dictionary
        return analysis

class DirectorStyleDatabase:
    def __init__(self, styles_file: str = "director_styles.json"):
        self.styles_file = styles_file
        self.styles = self._load_styles()

    def _load_styles(self) -> Dict[str, Any]:
        if os.path.exists(self.styles_file):
            with open(self.styles_file, 'r') as f:
                return json.load(f)
        return {}

    def get_style(self, style_name: str) -> Dict[str, Any]:
        return self.styles.get(style_name, {})

    def add_style(self, style_name: str, style_data: Dict[str, Any]) -> None:
        self.styles[style_name] = style_data
        self._save_styles()

    def _save_styles(self) -> None:
        with open(self.styles_file, 'w') as f:
            json.dump(self.styles, f)

class PromptGenerator:
    def __init__(self, llm):
        self.llm = llm

    async def generate_prompt(self, scene_analysis: Dict[str, Any], director_style: Dict[str, Any]) -> str:
        generate_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["scene_analysis", "director_style"],
                template="Given the following scene analysis and director's style, generate a detailed visual prompt for an AI image generator:\n\nScene Analysis: {scene_analysis}\n\nDirector's Style: {director_style}\n\nVisual Prompt:"
            )
        )
        result = await generate_chain.arun({
            "scene_analysis": json.dumps(scene_analysis),
            "director_style": json.dumps(director_style)
        })
        return result

class OutputFormatter:
    def format_output(self, scenes: List[Dict[str, Any]], prompts: List[str]) -> str:
        # Implement logic to format the scenes and prompts into a spreadsheet-like output
        # This is a placeholder and should be implemented based on the desired output format
        output = "Scene,Prompt\n"
        for scene, prompt in zip(scenes, prompts):
            output += f"{scene['description']},{prompt}\n"
        return output

class PromptForgeCore:
    def __init__(self, model_name: str = "gpt-4-1106-preview"):
        self.meta_chain = MetaChain(self, model_name)
        self.style_handler = StyleHandler()
        self.shot_description = ""
        self.directors_notes = ""
        self.script = ""
        self.highlighted_text = ""
        self.stick_to_script = False
        self.subjects: List[Dict[str, Any]] = []
        self.available_models = self.get_available_models()

    @staticmethod
    async def get_available_models() -> List[str]:
        try:
            models = await client.models.list()
            chat_models = [model.id for model in models if model.id.startswith("gpt")]
            if not chat_models:
                raise ValueError("No GPT chat models found")
            return chat_models
        except Exception as e:
            logging.error(f"Error fetching OpenAI models: {str(e)}")
            return ["gpt-3.5-turbo", "gpt-4"]  # Fallback to current default chat models

    def set_style(self, style: str) -> None:
        self.style_handler.set_prefix(style)

    def set_model(self, model_name: str) -> None:
        self.meta_chain.set_model(model_name)

    def process_shot(self, shot_description: str) -> None:
        self.shot_description = shot_description

    def process_directors_notes(self, notes: str) -> None:
        self.directors_notes = notes

    def process_script(self, highlighted_text: str, full_script: str, stick_to_script: bool) -> None:
        self.highlighted_text = highlighted_text.strip() if highlighted_text else full_script
        self.script = full_script.strip()
        self.stick_to_script = stick_to_script

    async def generate_prompt(self, length: str, shot_description: str, style: str, camera_move: str, 
                              directors_notes: str, script: str, stick_to_script: bool) -> str:
        try:
            active_subjects = [subject for subject in self.subjects if subject.get('active', False)]
            
            # Prepare the base prompt
            base_prompt = f"""
**Visual Prompt:**

**Shot Description:** {shot_description}

**Style:** {style}

**Camera Move:** {camera_move}

**Director's Notes:** {directors_notes}

**Active Subjects:**
{self._format_active_subjects(active_subjects)}
"""
            
            if stick_to_script:
                base_prompt += f"\n**Script:** {script}"
            
            # Generate prompts of different lengths
            messages = [
                {"role": "system", "content": "You are a creative AI assistant that generates detailed visual prompts for image generation."},
                {"role": "user", "content": f"Based on the following information, generate short, medium, and long visual prompts:\n\n{base_prompt}\n\nProvide the prompts in the following format:\nShort Prompt: [Your short prompt here]\nMedium Prompt: [Your medium prompt here]\nLong Prompt: [Your long prompt here]"}
            ]
            
            response = await client.chat.completions.create(
                model=self.meta_chain.model_name,
                messages=messages,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7,
            )
            
            prompt = response.choices[0].message.content.strip()
            prompt = prompt.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Log the inputs and generated prompt
            inputs = {
                "length": length,
                "shot_description": shot_description,
                "style": style,
                "camera_move": camera_move,
                "directors_notes": directors_notes,
                "script": script,
                "stick_to_script": stick_to_script,
                "active_subjects": active_subjects
            }
            prompt_logger.log_prompt(inputs, prompt)
            
            # Log the inputs and generated prompt
            inputs = {
                "length": length,
                "shot_description": shot_description,
                "style": style,
                "camera_move": camera_move,
                "directors_notes": directors_notes,
                "script": script,
                "stick_to_script": stick_to_script,
                "active_subjects": active_subjects
            }
            prompt_logger.log_prompt(inputs, prompt)
            
            return prompt
        except Exception as e:
            logging.exception("Error in PromptForgeCore.generate_prompt")
            raise

    def save_prompt(self, prompt: str, components: Dict[str, Any]) -> None:
        self.meta_chain.prompt_manager.save_prompt(prompt, components)

    def add_subject(self, name: str, category: str, description: str) -> None:
        self.subjects.append({
            'name': name,
            'category': category,
            'description': description,
            'active': True
        })

    def remove_subject(self, name: str) -> None:
        self.subjects = [subject for subject in self.subjects if subject['name'] != name]

    def toggle_subject(self, name: str) -> None:
        for subject in self.subjects:
            if subject['name'] == name:
                subject['active'] = not subject['active']
                break

    def _format_active_subjects(self, active_subjects: List[Dict[str, Any]]) -> str:
        return "\n".join([f"- {s['name']} ({s['category']}): {s['description']}" for s in active_subjects])

    def get_director_styles(self) -> List[str]:
        return list(self.meta_chain.director_styles.keys())

    async def analyze_script(self, script_content: str, director_style: str) -> str:
        return await self.meta_chain.generate_prompt_spreadsheet(script_content, director_style)

# Example usage
async def main():
    core = PromptForgeCore()
    
    # Manual prompt generation
    core.set_style("Noir detective")
    core.add_subject("John", "Main Character", "A hardboiled detective with a troubled past")
    prompt = await core.generate_prompt("medium", "A dimly lit office, smoke curling from an ashtray", "Classic Noir", "Slow pan", "Emphasize the shadows", "", False)
    print("Single Prompt:", prompt)
    
    # Automated script processing
    script = """
    INT. DETECTIVE'S OFFICE - NIGHT
    
    JOHN, a grizzled detective, sits at his desk, staring at crime scene photos.
    A knock at the door startles him.
    
    JANE (O.S.)
    Detective? I need your help.
    
    John sighs, reaching for his gun.
    """
    
    output = await core.analyze_script(script, "Classic Noir")
    print("\nAutomated Script Processing Output:")
    print(output)

if __name__ == "__main__":
    asyncio.run(main())
