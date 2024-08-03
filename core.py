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
from typing import Dict, Any


from config import get_openai_api_key

# Get the API key from the config
openai_api_key = get_openai_api_key()

client = AsyncOpenAI(api_key=openai_api_key)

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
        self._initialize_saved_prompts()

    def _initialize_saved_prompts(self):
        if not os.path.exists("saved_prompts.json") or os.path.getsize("saved_prompts.json") == 0:
            with open("saved_prompts.json", "w") as f:
                json.dump([], f)
        self.temperature = 0.7  # Default temperature
        self.style_prefix = ""
        self.style_suffix = ""
        self.end_parameters = ""
        self.camera_shot = ""
        self.camera_move = ""
        self.history = deque(maxlen=10)  # Store last 10 states
        self.future = deque(maxlen=10)  # Store undone states for redo
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0.7)
        
        # Initialize StyleHandler
        self.style_handler = StyleHandler()
        
        # Initialize TemplateManager
        self.template_manager = TemplateManager()

    async def generate_subjects(self, script_text: str) -> List[Dict[str, Any]]:
        prompt = f"""
        Analyze the following script excerpt and perform these tasks:

        Identify key subjects (characters, locations, objects) crucial to the scene.
        For each subject, provide:

        A clear, concise name
        A category (Character, Location, or Object)
        A detailed description (50-100 words) that includes:
        - Physical attributes (appearance, size, color, etc.)
        - Emotional or atmospheric qualities
        - Relevance to the scene or story
        - Any unique features or characteristics

        Ensure descriptions are consistent with the script but expand beyond explicitly stated details.
        Present the information in a structured format for each subject:
        Name: [Subject Name]
        Category: [Category]
        Description: [Detailed description]

        Script excerpt: {script_text}
        """

        try:
            response = await self.llm.agenerate([prompt])
            subjects_text = response.generations[0][0].text

            subjects = []
            current_subject = {}
            for line in subjects_text.split('\n'):
                line = line.strip()
                if line.startswith('Name:'):
                    if current_subject:
                        subjects.append(current_subject)
                    current_subject = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('Category:'):
                    current_subject['category'] = line.split(':', 1)[1].strip()
                elif line.startswith('Description:'):
                    current_subject['description'] = line.split(':', 1)[1].strip()
                elif current_subject and 'description' in current_subject:
                    current_subject['description'] += ' ' + line

            if current_subject:
                subjects.append(current_subject)

            return subjects
        except Exception as e:
            logging.error(f"Error generating subjects: {str(e)}")
            raise

    def add_subject(self, name: str, category: str, description: str):
        self.subjects.append({
            'name': name,
            'category': category,
            'description': description,
            'active': True
        })

    def generate_subjects(self, script_text: str) -> List[Dict[str, Any]]:
        prompt = f"""
        Analyze the following script excerpt and perform these tasks:

        Identify key subjects (characters, locations, objects) crucial to the scene.
        For each subject, provide:

        A clear, concise name
        A category (Character, Location, or Object)
        A detailed description (50-100 words) that includes:
        - Physical attributes (appearance, size, color, etc.)
        - Emotional or atmospheric qualities
        - Relevance to the scene or story
        - Any unique features or characteristics

        Ensure descriptions are consistent with the script but expand beyond explicitly stated details.
        Present the information in a structured format for each subject:
        Name: [Subject Name]
        Category: [Category]
        Description: [Detailed description]

        Script excerpt: {script_text}
        """

        try:
            response = self.llm.generate([prompt])
            subjects_text = response.generations[0][0].text

            subjects = []
            current_subject = {}
            for line in subjects_text.split('\n'):
                if line.startswith('Name:'):
                    if current_subject:
                        subjects.append(current_subject)
                    current_subject = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('Category:'):
                    current_subject['category'] = line.split(':', 1)[1].strip()
                elif line.startswith('Description:'):
                    current_subject['description'] = line.split(':', 1)[1].strip()

            if current_subject:
                subjects.append(current_subject)

            return subjects
        except Exception as e:
            logging.error(f"Error generating subjects: {str(e)}")
            return []

    def add_subject(self, name: str, category: str, description: str):
        self.subjects.append({
            'name': name,
            'category': category,
            'description': description,
            'active': True
        })

    async def generate_subjects(self, script_text: str) -> List[Dict[str, Any]]:
        prompt = f"""
        Analyze the following script excerpt and perform these tasks:

        Identify key subjects (characters, locations, objects) crucial to the scene.
        For each subject, provide:

        A clear, concise name
        A category (Character, Location, or Object)
        A detailed description (50-100 words) that includes:
        - Physical attributes (appearance, size, color, etc.)
        - Emotional or atmospheric qualities
        - Relevance to the scene or story
        - Any unique features or characteristics

        Ensure descriptions are consistent with the script but expand beyond explicitly stated details.
        Present the information in a structured format for each subject:
        Name: [Subject Name]
        Category: [Category]
        Description: [Detailed description]

        Script excerpt: {script_text}
        """

        response = await self.llm.agenerate([prompt])
        subjects_text = response.generations[0][0].text

        subjects = []
        current_subject = {}
        for line in subjects_text.split('\n'):
            if line.startswith('Name:'):
                if current_subject:
                    subjects.append(current_subject)
                current_subject = {'name': line.split(':', 1)[1].strip()}
            elif line.startswith('Category:'):
                current_subject['category'] = line.split(':', 1)[1].strip()
            elif line.startswith('Description:'):
                current_subject['description'] = line.split(':', 1)[1].strip()

        if current_subject:
            subjects.append(current_subject)

        return subjects

    def add_subject(self, name: str, category: str, description: str):
        self.subjects.append({
            'name': name,
            'category': category,
            'description': description,
            'active': True
        })

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

    def _save_state(self, state=None):
        if state is None:
            state = self._get_current_state()
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
        self.temperature = state['temperature']

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
            'subjects': self.subjects,
            'camera_shot': self.camera_shot,
            'temperature': self.temperature,
            'camera_move': self.camera_move
        }

class TemplateManager:
    def __init__(self, template_file: str = "prompt_templates.json"):
        self.template_file = template_file
        self.templates = self._load_templates()

    def save_template(self, name: str, components: Dict[str, Any]):
        self.templates[name] = components
        self._save_templates()

    def load_template(self, name: str) -> Dict[str, Any]:
        return self.templates.get(name, {})

    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        return self.templates

    def delete_template(self, name: str):
        if name in self.templates:
            del self.templates[name]
            self._save_templates()

    def update_template(self, name: str, components: Dict[str, Any]):
        if name in self.templates:
            self.templates[name] = components
            self._save_templates()

    def _save_templates(self):
        with open(self.template_file, 'w') as f:
            json.dump(self.templates, f)

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.template_file):
            with open(self.template_file, 'r') as f:
                return json.load(f)
        return {}

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
        self._initialize_saved_prompts()
        self.temperature = 0.7  # Default temperature
        self.style_prefix = ""
        self.style_suffix = ""
        self.end_parameters = ""
        self.camera_shot = ""
        self.camera_move = ""
        self.history = deque(maxlen=10)  # Store last 10 states
        self.future = deque(maxlen=10)  # Store undone states for redo
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0.7)
        
        # Initialize StyleHandler
        self.style_handler = StyleHandler()
        
        # Initialize TemplateManager
        self.template_manager = TemplateManager()

    def _save_state(self, state=None):
        if state is None:
            state = self._get_current_state()
        self.history.append(state)
        self.future.clear()  # Clear redo stack when a new action is performed

    def _initialize_saved_prompts(self):
        if not os.path.exists("saved_prompts.json") or os.path.getsize("saved_prompts.json") == 0:
            with open("saved_prompts.json", "w") as f:
                json.dump([], f)

    async def generate_prompt(self, style: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str) -> Dict[str, str]:
        try:
            active_subjects = [subject for subject in self.subjects if subject.get('active', False)]
            
            # Generate prompts using MetaChain
            full_prompt = await self.meta_chain.generate_prompt(
                active_subjects=active_subjects,
                style=style,
                shot_description=shot_description,
                directors_notes=directors_notes,
                highlighted_text=highlighted_text,
                full_script=script if stick_to_script else "",
                end_parameters=end_parameters
            )
            
            # Generate different lengths of prompts
            concise_prompt = self._generate_concise_prompt(full_prompt)
            normal_prompt = self._generate_normal_prompt(full_prompt)
            detailed_prompt = full_prompt

            prompts = {
                "Concise Prompt": concise_prompt,
                "Normal Prompt": normal_prompt,
                "Detailed Prompt": detailed_prompt
            }
            
            # Log the inputs and generated outputs
            inputs = {
                "shot_description": shot_description,
                "style": style,
                "directors_notes": directors_notes,
                "script": script if stick_to_script else "",
                "stick_to_script": stick_to_script,
                "active_subjects": [s['name'] for s in active_subjects],
                "end_parameters": end_parameters
            }
            for length, prompt in prompts.items():
                self.prompt_logger.log_prompt({**inputs, "length": length}, prompt)
            
            return prompts
        except Exception as e:
            logging.exception("Error in PromptForgeCore.generate_prompt")
            raise

    def _generate_concise_prompt(self, full_prompt: str) -> str:
        # Extract the first sentence or up to 100 characters
        concise = full_prompt.split('.')[0]
        return concise[:100] + ('...' if len(concise) > 100 else '')

    def _generate_normal_prompt(self, full_prompt: str) -> str:
        # Extract the first paragraph or up to 250 characters
        normal = full_prompt.split('\n\n')[0]
        return normal[:250] + ('...' if len(normal) > 250 else '')

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

    def edit_subject(self, index: int, name: str, category: str, description: str) -> None:
        if 0 <= index < len(self.subjects):
            self.subjects[index] = {
                'name': name,
                'category': category,
                'description': description,
                'active': self.subjects[index]['active']
            }
        else:
            raise IndexError("Subject index out of range")

    def _format_active_subjects(self, active_subjects: List[Dict[str, Any]]) -> str:
        return "\n".join([f"- {s['name']} ({s['category']}): {s['description']}" for s in active_subjects])

    def get_director_styles(self) -> List[str]:
        return list(self.meta_chain.director_styles.keys())

    async def analyze_script(self, script_content: str, director_style: str) -> str:
        return await self.meta_chain.generate_prompt_spreadsheet(script_content, director_style)

# End of PromptForgeCore class
