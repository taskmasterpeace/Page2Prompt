from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from typing import Dict, List
import logging
class ScriptAnalyzer:
    def __init__(self):
        self.entities = {}
        self.context = {}
        self.llm = OpenAI(temperature=0.3)

    def analyze_script(self, script: str):
        entity_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["script"],
                template="Analyze the following script and identify key entities (characters, locations, objects) and their descriptions:\n\n{script}\n\nEntities:"
            )
        )
        context_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["script"],
                template="Analyze the following script and provide a summary of the context, themes, and overall atmosphere:\n\n{script}\n\nContext Summary:"
            )
        )

        entity_result = entity_chain({"script": script})
        context_result = context_chain({"script": script})

        self.entities = self._parse_entities(entity_result["text"])
        self.context = self._parse_context(context_result["text"])

    def get_entity_description(self, entity_name: str) -> str:
        return self.entities.get(entity_name, "")

    def get_context_up_to_point(self, point: str) -> str:
        # For simplicity, we're returning the full context
        # In a more advanced implementation, you could split the script into scenes
        # and return context up to the scene containing the given point
        return self.context.get("summary", "")

    def _parse_entities(self, entities_text: str) -> Dict[str, str]:
        entities = {}
        current_entity = ""
        current_description = ""
        for line in entities_text.split('\n'):
            if ':' in line:
                if current_entity:
                    entities[current_entity] = current_description.strip()
                current_entity, current_description = line.split(':', 1)
                current_entity = current_entity.strip()
                current_description = current_description.strip()
            else:
                current_description += " " + line.strip()
        if current_entity:
            entities[current_entity] = current_description.strip()
        return entities

    def _parse_context(self, context_text: str) -> Dict[str, str]:
        context = {"summary": context_text.strip()}
        # In a more advanced implementation, you could parse out specific themes,
        # atmosphere, etc. into separate keys in the context dictionary
        return context