import asyncio
import logging
from typing import Dict, List
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None  # Initialize as None
        self.director_styles = {"Default": {}}  # Add more styles as needed

    async def generate_prompt(self, style: str, highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, active_subjects: list = None, full_script: str = "", temperature: float = 0.7) -> Dict[str, Dict[str, str]]:
        try:
            self._initialize_llm(temperature)
            subject_info = self._format_subject_info(active_subjects)
            
            style_prefix = style.split('--')[0].strip() if '--' in style else style
            style_suffix = style.split('--')[1].strip() if '--' in style else ""
            
            templates = {
                "concise": self._get_prompt_template("concise (about 20 words)"),
                "normal": self._get_prompt_template("normal (about 50 words)"),
                "detailed": self._get_prompt_template("detailed (about 100 words)")
            }

            results = {}
            for length, template in templates.items():
                chain = RunnableSequence(template | self.llm)
                try:
                    result = await chain.ainvoke({
                        "style_prefix": style_prefix,
                        "style_suffix": style_suffix,
                        "shot_description": shot_description,
                        "directors_notes": directors_notes,
                        "highlighted_text": highlighted_text,
                        "full_script": full_script,
                        "subject_info": subject_info,
                        "end_parameters": end_parameters,
                        "stick_to_script": stick_to_script,
                        "length": length
                    })
                    structured_output = self._structure_prompt_output(result.content)
                    full_prompt = f"{style_prefix} {structured_output['Full Prompt']} {style_suffix} {end_parameters}".strip()
                    structured_output['Full Prompt'] = full_prompt
                    results[length] = structured_output
                except Exception as e:
                    raise PromptGenerationError(f"Error invoking model for {length} prompt: {str(e)}")

            return results
        except Exception as e:
            logging.exception("Error in MetaChain.generate_prompt")
            raise PromptGenerationError(f"Failed to generate prompt: {str(e)}")

    def _get_prompt_template(self, length: str) -> PromptTemplate:
        base_template = """
        Generate a {length} prompt based on the following information:
        Subjects: {subject_info}
        Style Prefix: {style_prefix}
        Style Suffix: {style_suffix}
        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Highlighted Script: {highlighted_text}
        Full Script: {full_script}
        End Parameters: {end_parameters}

        {'Strictly adhere to the provided script.' if stick_to_script else 'Use the script as inspiration, but feel free to be creative.'}

        The prompt should follow this structure:
        [Subject] [Action/Pose] in [Context/Setting], [Time of Day], [Weather Conditions], [Composition], [Foreground Elements], [Background Elements], [Mood/Atmosphere], [Props/Objects], [Environmental Effects]

        Important: Describe the scene positively. Don't use phrases like "no additional props" or "no objects present". Instead, focus on what is in the scene.

        Generate a structured output with the following fields:
        1. Subject
        2. Action/Pose
        3. Context/Setting
        4. Time of Day
        5. Weather Conditions
        6. Composition
        7. Foreground Elements
        8. Background Elements
        9. Mood/Atmosphere
        10. Props/Objects
        11. Environmental Effects
        12. Full Prompt

        {length} Prompt:
        """

        return PromptTemplate(
            input_variables=["style_prefix", "style_suffix", "shot_description", "directors_notes", "highlighted_text", "full_script", "subject_info", "end_parameters", "stick_to_script", "length"],
            template=base_template
        )

    def _format_subject_info(self, active_subjects: List[Dict]) -> str:
        if not active_subjects:
            return "No active subjects"
        return ", ".join([f"{s.get('name', '')} ({s.get('category', '')}: {s.get('description', '')})" for s in active_subjects])

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
