import asyncio
import logging
from typing import Dict, List, Optional, Union
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from gradio_meta_chain_exceptions import PromptGenerationError, ScriptAnalysisError

class MetaChain:
    def __init__(self, core):
        self.core = core
        self.llm = None  # Initialize as None
        self.director_styles = {"Default": {}}  # Add more styles as needed

    def _initialize_llm(self, temperature: float):
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=temperature)

    async def generate_prompt(self, style: Optional[str], highlighted_text: str, shot_description: str, directors_notes: str, script: str, stick_to_script: bool, end_parameters: str, active_subjects: list = None, full_script: str = "", temperature: float = 0.7) -> Dict[str, Dict[str, str]]:
        logging.info(f"Generating prompt with inputs: style={style}, highlighted_text={highlighted_text}, shot_description={shot_description}, directors_notes={directors_notes}, script={script}, stick_to_script={stick_to_script}, end_parameters={end_parameters}, active_subjects={active_subjects}, full_script={full_script}, temperature={temperature}")
        try:
            self._initialize_llm(temperature)
            subject_info = self._format_subject_info(active_subjects)
            
            style = style or ""  # Set style to an empty string if it's None
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
                    script_adherence = 'Strictly adhere to the provided script.' if stick_to_script else 'Use the script as inspiration, but feel free to be creative.'
                    input_data = {
                        "style_prefix": style_prefix,
                        "style_suffix": style_suffix,
                        "shot_description": shot_description,
                        "directors_notes": directors_notes,
                        "highlighted_text": highlighted_text,
                        "full_script": full_script,
                        "subject_info": subject_info,
                        "end_parameters": end_parameters,
                        "script_adherence": script_adherence,
                        "length": length
                    }
                    logging.info(f"Invoking chain for {length} prompt with input: {input_data}")
                    result = await chain.ainvoke(input_data)
                    logging.info(f"Chain result for {length}: {result.content}")
                    structured_output = self._structure_prompt_output(result.content)
                    full_prompt = f"{style_prefix} {structured_output['Full Prompt']} {style_suffix} {end_parameters}".strip()
                    structured_output['Full Prompt'] = full_prompt
                    results[length] = structured_output
                except KeyError as e:
                    logging.error(f"KeyError in generate_prompt for {length}: {str(e)}")
                    results[length] = {"Full Prompt": f"Error: Missing key {str(e)} in model output"}
                except Exception as e:
                    logging.error(f"Unexpected error in generate_prompt for {length}: {str(e)}")
                    results[length] = {"Full Prompt": f"Error: {str(e)}"}

            logging.info(f"Generated prompts: {results}")
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

        {script_adherence}

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
            input_variables=["style_prefix", "style_suffix", "shot_description", "directors_notes", "highlighted_text", "full_script", "subject_info", "end_parameters", "script_adherence", "length"],
            template=base_template
        )

    def _format_subject_info(self, active_subjects: Optional[List[Dict]]) -> str:
        if not active_subjects:
            return "No active subjects"
        return ", ".join([f"{s.get('name', '')} ({s.get('category', '')}: {s.get('description', '')})" for s in active_subjects if isinstance(s, dict)])

    def _structure_prompt_output(self, content: str) -> Dict[str, str]:
        lines = content.strip().split('\n')
        structured_output = {
            "Subject": "", "Action/Pose": "", "Context/Setting": "", "Time of Day": "",
            "Weather Conditions": "", "Composition": "", "Foreground Elements": "",
            "Background Elements": "", "Mood/Atmosphere": "", "Props/Objects": "",
            "Environmental Effects": "", "Full Prompt": ""
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
            structured_output["Full Prompt"] = " ".join(structured_output.values())
        
        return structured_output

    async def analyze_script(self, script: str, director_style: str):
        try:
            # Placeholder for script analysis logic
            # This should be implemented based on your specific requirements
            return f"Analysis of script using {director_style} style:\n{script[:100]}..."
        except Exception as e:
            raise ScriptAnalysisError(str(e))
