# core.py

import asyncio
from typing import List, Dict, Optional, Tuple, Any
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI
from meta_chain import MetaChain
import logging
from langchain_core.prompts import PromptTemplate
import json
import os
from openai import AsyncOpenAI
import json
from datetime import datetime
from styles import StyleManager
import random
from collections import deque


from config import get_openai_api_key, get_langsmith_api_key

# Get the API keys from the config
openai_api_key = get_openai_api_key()
langsmith_api_key = get_langsmith_api_key()

client = AsyncOpenAI(api_key=openai_api_key)

# Set up LangSmith (you'll need to import and use it where needed)
os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key

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

class PromptLogger:
    def __init__(self, log_file="prompt_log.json"):
        self.log_file = log_file

    def log_prompt(self, inputs: Dict[str, Any], generated_prompt: str):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "inputs": inputs,
            "generated_prompt": generated_prompt
        }
        with open(self.log_file, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

    def get_logs(self):
        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                logs.append(json.loads(line))
        return logs

class PromptForgeCore:
    def __init__(self):
        self.meta_chain = MetaChain(self)
        self.style_manager = StyleManager()
        self.shot_description = ""
        self.directors_notes = ""
        self.script = ""
        self.highlighted_text = ""
        self.stick_to_script = False
        self.subjects: List[Dict[str, Any]] = []
        self.prompt_logger = PromptLogger("prompt_log.json")
        self.style_prefix = ""
        self.style_suffix = ""
        self.end_parameters = ""
        self.history = deque(maxlen=10)  # Store last 10 states
        self.future = deque(maxlen=10)  # Store undone states for redo
        self.llm = ChatOpenAI(temperature=0.7)

    def generate_style_details(self, prefix: str) -> str:
        style_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["style"],
                template="Given the style '{style}', generate three distinct and detailed visual descriptors that characterize this style. Focus on unique elements, color palettes, lighting, and overall atmosphere. Separate each descriptor with a semicolon:"
            )
        )
        result = style_chain.run({"style": prefix})
        return result.strip()

    def get_logs(self):
        return self.prompt_logger.get_logs()

    def set_style(self, style: str) -> None:
        self._save_state()
        self.style_handler.set_prefix(style)

    def process_shot(self, shot_description: str) -> None:
        self._save_state()
        self.shot_description = shot_description

    def process_directors_notes(self, notes: str) -> None:
        self._save_state()
        self.directors_notes = notes

    def process_script(self, highlighted_text: str, full_script: str, stick_to_script: bool) -> None:
        self._save_state()
        self.highlighted_text = highlighted_text.strip() if highlighted_text else full_script
        self.script = full_script.strip()
        self.stick_to_script = stick_to_script

    def _save_state(self):
        state = {
            'shot_description': self.shot_description,
            'directors_notes': self.directors_notes,
            'script': self.script,
            'highlighted_text': self.highlighted_text,
            'stick_to_script': self.stick_to_script,
            'style_prefix': self.style_prefix,
            'style_suffix': self.style_suffix,
            'end_parameters': self.end_parameters,
            'subjects': self.subjects.copy()  # Add subjects to the state
        }
        self.history.append(state)
        self.future.clear()  # Clear redo stack when a new action is performed

    def undo(self):
        if len(self.history) > 1:  # Keep at least one state in history
            current_state = self.history.pop()
            self.future.appendleft(current_state)
            previous_state = self.history[-1]
            self._restore_state(previous_state)
        return self._get_current_state()

    def redo(self):
        if self.future:
            next_state = self.future.popleft()
            self.history.append(next_state)
            self._restore_state(next_state)
        return self._get_current_state()

    def _restore_state(self, state):
        self.shot_description = state['shot_description']
        self.directors_notes = state['directors_notes']
        self.script = state['script']
        self.highlighted_text = state['highlighted_text']
        self.stick_to_script = state['stick_to_script']
        self.style_prefix = state['style_prefix']
        self.style_suffix = state['style_suffix']
        self.end_parameters = state['end_parameters']
        self.subjects = state['subjects'].copy()  # Restore subjects

    def _get_current_state(self):
        return {
            'shot_description': self.shot_description,
            'directors_notes': self.directors_notes,
            'script': self.script,
            'highlighted_text': self.highlighted_text,
            'stick_to_script': self.stick_to_script,
            'style_prefix': self.style_prefix,
            'style_suffix': self.style_suffix,
            'end_parameters': self.end_parameters,
            'subjects': self.subjects
        }

    async def generate_prompt(self, shot_description: str, style_prefix: str, style_suffix: str, camera_shot: str, camera_move: str, 
                        directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, length: str = "medium") -> str:
        try:
            active_subjects = [subject for subject in self.subjects if subject.get('active', False)]
            
            # Prepare the base prompt with all information
            base_prompt = f"""
Create a detailed, vivid description for an AI image generator based on the following information:

Style: {style_prefix}

Shot Description: {shot_description}

Director's Notes: {directors_notes}

Active Subjects:
{self._format_active_subjects(active_subjects)}

Camera Shot: {camera_shot}
Camera Move: {camera_move}

Desired Prompt Length: {length}

Additional Context:
- Focus on creating a visually rich and atmospheric scene.
- Describe the lighting, colors, and textures in detail.
- Emphasize the mood and emotion of the scene.
- Include specific details about the characters' appearances and expressions.
- Describe the environment and any important objects in the scene.
"""
            
            if stick_to_script:
                base_prompt += f"\nRelevant Script Excerpt: {script}\n- Ensure the description aligns closely with this script excerpt."
            
            # Generate a comprehensive content prompt
            messages = [
                {"role": "system", "content": "You are a highly skilled cinematographer and visual artist. Your task is to create detailed, evocative descriptions for AI image generation, focusing on visual elements, atmosphere, and capturing the essence of the scene."},
                {"role": "user", "content": base_prompt}
            ]
            
            response = await client.chat.completions.create(
                model=self.meta_chain.model_name,
                messages=messages,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.8,
            )
            
            content_prompt = response.choices[0].message.content.strip()
            content_prompt = content_prompt.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Combine all prompt components
            full_prompt = f"{content_prompt}\n\n{style_suffix}"
            
            if end_parameters:
                full_prompt += f"\n\n{end_parameters}"
            
            # Generate FileList of needed elements
            file_list = await self._generate_file_list(active_subjects, shot_description, script)
            full_prompt += f"\n\nFileList of needed elements:\n{file_list}"
            
            # Log the inputs and generated prompt
            inputs = {
                "shot_description": shot_description,
                "style_prefix": style_prefix,
                "style_suffix": style_suffix,
                "camera_shot": camera_shot,
                "camera_move": camera_move,
                "directors_notes": directors_notes,
                "script": script,
                "stick_to_script": stick_to_script,
                "active_subjects": [s['name'] for s in active_subjects],  # Only log subject names
                "end_parameters": end_parameters,
                "length": length
            }
            self.prompt_logger.log_prompt(inputs, full_prompt)
            
            return full_prompt
        except Exception as e:
            logging.exception("Error in PromptForgeCore.generate_prompt")
            raise

    async def _generate_file_list(self, active_subjects, shot_description, script):
        # Combine all text to analyze
        all_text = f"{shot_description}\n{script}\n" + "\n".join([f"{s['name']}: {s['description']}" for s in active_subjects])
        
        # Use GPT to generate the file list
        messages = [
            {"role": "system", "content": "You are an AI assistant that identifies key elements in a scene description and generates a list of image files that would be needed to create the scene."},
            {"role": "user", "content": f"Based on the following scene description, generate a list of image files that would be needed to create this scene. Focus on characters, objects, and settings. Format the list as 'element.png' for each item:\n\n{all_text}"}
        ]
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5,
        )
        
        file_list = response.choices[0].message.content.strip()
        return file_list

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
async def initialize(self):
    # Initialize any necessary components
    self.style_handler = StyleHandler()
    # Add any other initialization steps here

async def main():
    core = PromptForgeCore()
    await core.initialize()
    
    # Manual prompt generation
    core.set_style("Noir detective")
    core.add_subject("John", "Main Character", "A hardboiled detective with a troubled past")
    prompt = await core.generate_prompt("A dimly lit office, smoke curling from an ashtray", "Classic Noir", core.style_handler.get_full_style(), "Slow pan", "Emphasize the shadows", "", "", False, core.end_parameters)
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

# Remove the if __name__ == "__main__" block from here
