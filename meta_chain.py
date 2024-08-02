# meta_chain.py

# meta_chain.py

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.chains import LLMChain
import json
from typing import List, Dict, Optional
import logging
import os
from prompt_manager import PromptManager

class DirectorStyle:
    def __init__(self, name: str, camera_techniques: List[str], visual_aesthetics: List[str], 
                 pacing: str, shot_compositions: List[str]):
        self.name = name
        self.camera_techniques = camera_techniques
        self.visual_aesthetics = visual_aesthetics
        self.pacing = pacing
        self.shot_compositions = shot_compositions

    def to_dict(self):
        return {
            "name": self.name,
            "camera_techniques": self.camera_techniques,
            "visual_aesthetics": self.visual_aesthetics,
            "pacing": self.pacing,
            "shot_compositions": self.shot_compositions
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            camera_techniques=data["camera_techniques"],
            visual_aesthetics=data["visual_aesthetics"],
            pacing=data["pacing"],
            shot_compositions=data["shot_compositions"]
        )

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.model_name = "gpt-4o-mini"
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=0.7)
        self.director_styles = {"Default": {}}  # Add more styles as needed
        self.prompt_manager = PromptManager()

    async def generate_prompt(self, active_subjects: list = None,
                              style: str = "", shot_description: str = "", directors_notes: str = "",
                              highlighted_text: str = "", full_script: str = "", end_parameters: str = "") -> Dict[str, str]:
        try:
            subject_info = self._format_subject_info(active_subjects)
            
            templates = {
                "concise": self._get_prompt_template("concise (about 12 words)"),
                "normal": self._get_prompt_template("normal (about 40 words)"),
                "detailed": self._get_prompt_template("detailed (about 80 words)")
            }

            results = {}
            for length, template in templates.items():
                chain = RunnableSequence(template | self.llm)
                result = await chain.ainvoke({
                    "style": style,
                    "shot_description": shot_description,
                    "directors_notes": directors_notes,
                    "highlighted_text": highlighted_text,
                    "full_script": full_script,
                    "subject_info": subject_info,
                    "end_parameters": end_parameters,
                    "length": length
                })
                results[length] = result.content.strip()

            # Post-process the results
            for length, prompt in results.items():
                prompt = prompt.replace("Concise Prompt:", "").replace("Normal Prompt:", "").replace("Detailed Prompt:", "").strip()
                results[length] = f"{style} {prompt} {end_parameters}".strip()

            return results
        except Exception as e:
            logging.exception("Error in MetaChain.generate_prompt")
            raise

    def _get_prompt_template(self, length: str) -> PromptTemplate:
        base_template = """
        Generate a {length} prompt based on the following information:
        Subjects: {subject_info}
        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Highlighted Script: {highlighted_text}
        Full Script: {full_script}

        The prompt should follow this structure:
        {style} [Subject] [Action/Pose] in [Context/Setting], [Time of Day], [Weather Conditions], [Composition], [Foreground Elements], [Background Elements], [Mood/Atmosphere], [Props/Objects], [Environmental Effects] {end_parameters}

        {length} Prompt:
        """

        return PromptTemplate(
            input_variables=["style", "shot_description", "directors_notes", "highlighted_text", "full_script", "subject_info", "end_parameters", "length"],
            template=base_template
        )

    def _format_subject_info(self, active_subjects: List[Dict]) -> str:
        if not active_subjects:
            return "No active subjects"
        return "\n".join([f"- {s['name']} ({s['category']}): {s['description']}" for s in active_subjects])

    def analyze_script(self, script: str, director_style: str) -> List[Dict]:
        scenes = self.core.script_analyzer.analyze_script(script)
        style = self.get_director_style(director_style)
        
        prompts = []
        for scene in scenes:
            prompt = self.generate_prompt(
                length="medium",
                active_subjects=scene.get("characters", []),
                director_style=director_style
            )
            prompts.append({
                "scene_number": scene["scene_number"],
                "scene_description": scene["description"],
                "generated_prompt": prompt
            })
        
        return prompts

    def generate_prompt_spreadsheet(self, script: str, director_style: str) -> str:
        prompts = self.analyze_script(script, director_style)
        
        # Here you would implement the logic to create a spreadsheet
        # For simplicity, we'll just return a formatted string
        output = "Scene Number | Scene Description | Generated Prompt\n"
        output += "-" * 80 + "\n"
        for prompt in prompts:
            output += f"{prompt['scene_number']} | {prompt['scene_description'][:30]}... | {prompt['generated_prompt'][:50]}...\n"
        
        return output

    def refine_prompt(self, initial_prompt: str, feedback: str) -> str:
        refine_template = PromptTemplate(
            input_variables=["initial_prompt", "feedback"],
            template="""
            Initial Prompt: {initial_prompt}
            
            User Feedback: {feedback}
            
            Based on the initial prompt and the user's feedback, generate a refined visual prompt that addresses the feedback while maintaining the core elements of the original prompt.
            
            Refined Prompt:
            """
        )

        refine_chain = RunnableSequence(refine_template | self.llm)
        result = refine_chain.invoke({
            "initial_prompt": initial_prompt,
            "feedback": feedback
        })

        return result.content

    def generate_variations(self, base_prompt: str, num_variations: int = 3) -> List[str]:
        variation_template = PromptTemplate(
            input_variables=["base_prompt", "num_variations"],
            template="""
            Base Prompt: {base_prompt}
            
            Generate {num_variations} variations of the above prompt, each maintaining the core elements but with different focuses or slight alterations in style or atmosphere.
            
            Variations:
            """
        )

        variation_chain = RunnableSequence(variation_template | self.llm)
        result = variation_chain.invoke({
            "base_prompt": base_prompt,
            "num_variations": num_variations
        })

        # Parse the results into a list of variations
        variations = result.content.split('\n')
        variations = [v.strip() for v in variations if v.strip()]
        return variations[:num_variations]  # Ensure we return the correct number of variations
