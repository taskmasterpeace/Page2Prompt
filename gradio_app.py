import gradio as gr
import asyncio
import json
import time
import csv
from gradio_config import Config
from gradio_prompt_manager import PromptManager
from gradio_styles import StyleManager
from gradio_script_analyzer import ScriptAnalyzer
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import MetaChainException, PromptGenerationError, ScriptAnalysisError
from debug_utils import logger, debug_func, get_error_report
from gradio_core import PromptForgeCore
from subject_manager import SubjectManager
from gradio_meta_chain import MetaChain


# Initialize components
config = Config()
core = PromptForgeCore()
prompt_manager = PromptManager()
style_manager = StyleManager()
script_analyzer = ScriptAnalyzer()
meta_chain = MetaChain(core)
core.meta_chain = meta_chain  # Set the meta_chain attribute of the PromptForgeCore instance
prompt_logger = PromptLogger()
subject_manager = SubjectManager()

# Load camera work options from CSV
def load_camera_work():
    camera_work = {'shot': [], 'move': [], 'size': []}
    with open('camera_work.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            camera_work[row['type']].append({'display': row['display'], 'insertion': row['insertion']})
    return camera_work

camera_work = load_camera_work()

@debug_func
async def generate_prompt_wrapper(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters, active_subjects, camera_shot, camera_move, camera_size, existing_prompts):
    try:
        # Validate and parse active_subjects
        active_subjects_list = []
        if active_subjects:
            for subject in active_subjects.split(','):
                parts = subject.strip().split(':')
                if len(parts) == 2:
                    name_category, description = parts
                    name, category = name_category.strip().split('(')
                    category = category.strip(')')
                    active_subjects_list.append({
                        "name": name.strip(),
                        "category": category.strip(),
                        "description": description.strip()
                    })
        
        result = await core.meta_chain.generate_prompt(
            style=style,
            highlighted_text=highlighted_text,
            shot_description=shot_description,
            directors_notes=directors_notes,
            script=script,
            stick_to_script=stick_to_script,
            end_parameters=end_parameters,
            active_subjects=active_subjects_list,
            full_script=script,
            camera_shot=camera_shot,
            camera_move=camera_move
        )
        prompt_logger.log_prompt(result)
        
        # Format the prompts
        concise = result.get("Concise Prompt", "")
        normal = result.get("Normal Prompt", "")
        detailed = result.get("Detailed Prompt", "")
        formatted_prompts = f"**Concise Prompt:**\n{concise}\n\n**Normal Prompt:**\n{normal}\n\n**Detailed Prompt:**\n{detailed}"
        
        # Append new prompts to existing prompts
        updated_prompts = existing_prompts + "\n\n" + formatted_prompts if existing_prompts else formatted_prompts
        
        return updated_prompts, json.dumps(result, indent=2), "Prompts generated successfully"
    except Exception as e:
        logger.exception("Unexpected error in generate_prompt_wrapper")
        return json.dumps({"error": str(e)}, indent=2)

@debug_func
async def analyze_script(script_content, director_style):
    try:
        result = await core.analyze_script(script_content, director_style)
        assert isinstance(result, str), f"analyze_script returned {type(result)}, expected str"
        return result
    except ScriptAnalysisError as e:
        logger.error(f"Script analysis failed: {str(e)}")
        return f"Error analyzing script: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected error in analyze_script")
        return f"Unexpected error: {str(e)}"

def save_prompt(concise_prompt, normal_prompt, detailed_prompt, name):
    try:
        prompt_manager.save_prompt({
            "concise": concise_prompt,
            "normal": normal_prompt,
            "detailed": detailed_prompt
        }, name, "", "", "", {})
        return f"Prompts '{name}' saved successfully."
    except Exception as e:
        return f"Error saving prompts: {str(e)}"

def get_prompt_logs():
    return prompt_logger.get_logs()

import random

def generate_random_style():
    adjectives = ["Vibrant", "Moody", "Ethereal", "Gritty", "Whimsical", "Minimalist", "Surreal", "Nostalgic", "Futuristic", "Retro"]
    nouns = ["Cityscape", "Nature", "Portrait", "Abstract", "Still Life", "Landscape", "Architecture", "Street Scene", "Macro", "Fantasy"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"

def save_style(style_name, prefix, suffix):
    if not style_name:
        return "Error: Style name cannot be empty."
    style_manager.add_style(style_name, prefix, suffix)
    return f"Style '{style_name}' saved successfully."

async def generate_style_details(prefix):
    return await core.meta_chain.generate_style_suffix(prefix)

async def generate_random_style_with_details():
    prefix = generate_random_style()
    suffix = await generate_style_details(prefix)
    return prefix, suffix

# Define Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# 🎬 Page 2 Prompt - Bring Your Script to Life")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Left column (Input)
            with gr.Group():
                gr.Markdown("## 📝 Shot Details")
                shot_description_input = gr.Textbox(label="📸 Shot Description", lines=2)
                directors_notes_input = gr.Textbox(label="🎭 Director's Notes", lines=3)
                active_subjects_input = gr.Textbox(label="👥 Active Subjects (comma-separated)")
            
            generate_button = gr.Button("🚀 Generate Prompt")

            with gr.Group():
                gr.Markdown("## 🎨 Style")
                with gr.Row():
                    style_input = gr.Dropdown(choices=style_manager.get_style_names(), label="Style", scale=1)
                    style_prefix_input = gr.Textbox(label="Style Prefix", placeholder="Enter style name/details", scale=2)
                    style_suffix_input = gr.Textbox(label="Style Suffix", placeholder="Enter style suffix", scale=2)
                with gr.Row():
                    save_style_button = gr.Button("💾 Save Style")
                    generate_style_details_button = gr.Button("🔍 Generate Style Details")
                    generate_random_style_button = gr.Button("🎲 Generate Random Style")
        
            def update_style_inputs(style_name):
                prefix, suffix = style_manager.get_style(style_name)
                return gr.Textbox.update(value=prefix), gr.Textbox.update(value=suffix)

            style_input.change(
                update_style_inputs,
                inputs=[style_input],
                outputs=[style_prefix_input, style_suffix_input]
            )
            
            script_input = gr.Textbox(label="📜 Script", lines=10)
            stick_to_script_input = gr.Checkbox(label="📌 Stick to Script")
            highlighted_text_input = gr.Textbox(label="🖍️ Highlighted Text", lines=3)
            
            with gr.Group():
                gr.Markdown("## 📷 Camera Settings")
                with gr.Row():
                    camera_shot_input = gr.Dropdown(label="🎥 Camera Shot", choices=[shot['display'] for shot in camera_work['shot']])
                    camera_move_input = gr.Dropdown(label="🎬 Camera Move", choices=[move['display'] for move in camera_work['move']])
                    camera_size_input = gr.Dropdown(label="📏 Camera Size", choices=[size['display'] for size in camera_work['size']])
            
            end_parameters_input = gr.Textbox(label="🔧 End Parameters")
            
            # Removed predictability_input

        with gr.Column(scale=1):
            # Right column (Generated Prompts)
            gr.Markdown("## 🖼️ Generated Prompts")
            generated_prompts = gr.Textbox(label="Generated Prompts", lines=15)
            structured_prompt = gr.JSON(label="Structured Prompt")
            generation_message = gr.Textbox(label="Generation Message")
    
            with gr.Row():
                save_button = gr.Button("💾 Save Prompts")
                copy_button = gr.Button("📋 Copy Prompts")
                clear_button = gr.Button("🧹 Clear All")
    
            feedback_area = gr.Textbox(label="💬 Feedback", interactive=False)
            
            with gr.Group():
                gr.Markdown("## 👤 Subject Details")
                subject_name = gr.Textbox(label="Subject Name")
                subject_category = gr.Dropdown(label="Subject Category", choices=["Person", "Animal", "Place", "Thing", "Other"])
                subject_description = gr.Textbox(label="Subject Description", lines=3)
                add_subject_button = gr.Button("➕ Add Subject")
                edit_subject_button = gr.Button("✏️ Edit Subject")
                remove_subject_button = gr.Button("🗑️ Remove Subject")
                subject_active = gr.Checkbox(label="Active in Scene")
                subjects_list = gr.JSON(label="Added Subjects")
                edit_subject_index = gr.Number(label="Index to Edit", value=-1, precision=0)
                remove_subject_index = gr.Number(label="Index to Remove", value=-1, precision=0)
    
    feedback_area = gr.Textbox(label="💬 Feedback", interactive=False)
    
    async def generate_prompt_wrapper(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters, active_subjects, camera_shot, camera_move, camera_size, existing_prompts, style_prefix, style_suffix):
        start_time = time.time()
        try:
            logger.info("Starting generate_prompt_wrapper")

            active_subjects_list = [subject.strip() for subject in active_subjects.split(',')] if active_subjects else []

            # Get the insertion text for camera work
            camera_shot_insertion = next((shot['insertion'] for shot in camera_work['shot'] if shot['display'] == camera_shot), '')
            camera_move_insertion = next((move['insertion'] for move in camera_work['move'] if move['display'] == camera_move), '')
            camera_size_insertion = next((size['insertion'] for size in camera_work['size'] if size['display'] == camera_size), '')

            # Combine camera work insertions
            camera_work_description = f"{camera_shot_insertion} {camera_move_insertion} {camera_size_insertion}".strip()

            meta_chain_start = time.time()
            result = await core.meta_chain.generate_prompt(
                style=style,
                highlighted_text=highlighted_text,
                shot_description=f"{shot_description}\n{camera_work_description}",
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                end_parameters=end_parameters,
                active_subjects=active_subjects_list,
                full_script=script,
                camera_shot=camera_shot,
                camera_move=camera_move,
                camera_size=camera_size
            )
            logger.info(f"meta_chain.generate_prompt took {time.time() - meta_chain_start:.2f} seconds")

            if not isinstance(result, dict):
                logger.error(f"Unexpected result type: {type(result)}")
                return "", json.dumps({"error": f"Unexpected result type {type(result)}"}), "Error: Unexpected result type"

            concise = result.get('Concise Prompt', '')
            normal = result.get('Normal Prompt', '')
            detailed = result.get('Detailed Prompt', '')

            def format_prompt(prefix, content, suffix):
                prefix = prefix.strip() if prefix else ""
                suffix = suffix.strip() if suffix else ""
                parts = [part for part in [prefix, content, suffix] if part]
                return " ".join(parts)

            all_prompts = f"Concise Prompt:\n{format_prompt(style_prefix, concise, style_suffix)}\n\nNormal Prompt:\n{format_prompt(style_prefix, normal, style_suffix)}\n\nDetailed Prompt:\n{format_prompt(style_prefix, detailed, style_suffix)}"

            logger.info(f"Prompts generated - Concise: {concise[:50]}..., Normal: {normal[:50]}..., Detailed: {detailed[:50]}...")

            formatted_prompts = f"**Concise Prompt:**\n{format_prompt(style_prefix, concise, style_suffix)}\n\n**Normal Prompt:**\n{format_prompt(style_prefix, normal, style_suffix)}\n\n**Detailed Prompt:**\n{format_prompt(style_prefix, detailed, style_suffix)}"
            return formatted_prompts, json.dumps(result, indent=2), "Prompts generated successfully"
        except Exception as e:
            logger.exception("Unexpected error in generate_prompt_wrapper")
            error_report = get_error_report()
            return "", json.dumps({"error": str(e), "error_report": error_report}), f"Error: {str(e)}"
        finally:
            logger.info(f"generate_prompt_wrapper took {time.time() - start_time:.2f} seconds total")

    generate_button.click(
        generate_prompt_wrapper,
        inputs=[style_input, highlighted_text_input, shot_description_input,
                directors_notes_input, script_input, stick_to_script_input,
                end_parameters_input, active_subjects_input,
                camera_shot_input, camera_move_input, camera_size_input, generated_prompts,
                style_prefix_input, style_suffix_input],
        outputs=[generated_prompts, structured_prompt, generation_message]
    )

    # Debug information section
    with gr.Group():
        gr.Markdown("## 🐛 Debug Information")
        debug_output = gr.Textbox(label="Debug Information", lines=10)
        with gr.Row():
            debug_button = gr.Button("Show Debug Info")
            clear_debug_button = gr.Button("Clear Debug Info")

        def show_debug_info():
            return get_error_report()

        def clear_debug_info():
            return ""

        debug_button.click(show_debug_info, inputs=[], outputs=[debug_output])
        clear_debug_button.click(clear_debug_info, inputs=[], outputs=[debug_output])
        
        def save_prompt_with_name(concise, normal, detailed, structured):
            name = gr.Textbox(label="Enter a name for this prompt set", interactive=True)
            save_button = gr.Button("Save")
            
            def do_save(name):
                if not name:
                    return "Please enter a name for the prompt set."
                prompt_manager.save_prompt({
                    "concise": concise,
                    "normal": normal,
                    "detailed": detailed,
                    "structured": structured
                }, name)
                return f"Prompt set '{name}' saved successfully."
            
            save_button.click(do_save, inputs=[name], outputs=feedback_area)

        save_button.click(
            save_prompt_with_name, 
            inputs=[generated_prompts, structured_prompt]
        )
        
        copy_button.click(lambda x: gr.Textbox.update(value=json.dumps(x, indent=2)), inputs=[structured_prompt], outputs=[feedback_area])
        
        def clear_all():
            return ("", "", "", "", "", False, "", "", "", "", "", "", "", "", "", "")
        
        clear_button.click(
            clear_all,
            outputs=[style_input, shot_description_input, directors_notes_input, highlighted_text_input,
                     script_input, stick_to_script_input, camera_shot_input, camera_move_input,
                     end_parameters_input, active_subjects_input, style_prefix_input, style_suffix_input,
                     subjects_list, generated_prompts, structured_prompt, generation_message]
        )

        subjects = []

        def add_subject(name, category, description):
            subjects.append({"name": name, "category": category, "description": description})
            return json.dumps(subjects, indent=2), "", "", ""

        def add_subject(name, category, description, active):
            subject_manager.add_subject(name, category, description, active)
            return json.dumps(subject_manager.subjects, indent=2), "", "", "", False

        def edit_subject(index, name, category, description, active):
            subject_manager.edit_subject(index, name, category, description, active)
            return json.dumps(subject_manager.subjects, indent=2), "", "", "", False

        def remove_subject(index):
            subject_manager.remove_subject(index)
            return json.dumps(subject_manager.subjects, indent=2)

        add_subject_button.click(
            add_subject,
            inputs=[subject_name, subject_category, subject_description, subject_active],
            outputs=[subjects_list, subject_name, subject_category, subject_description, subject_active]
        )

        edit_subject_button.click(
            edit_subject,
            inputs=[edit_subject_index, subject_name, subject_category, subject_description, subject_active],
            outputs=[subjects_list, subject_name, subject_category, subject_description, subject_active]
        )

        remove_subject_button.click(
            remove_subject,
            inputs=[remove_subject_index],
            outputs=[subjects_list]
        )
        
        # Style-related event handlers
        generate_random_style_button.click(
            lambda: asyncio.run(generate_random_style_with_details()),
            outputs=[style_prefix_input, style_suffix_input]
        )
        save_style_button.click(save_style, inputs=[style_input, style_prefix_input, style_suffix_input], outputs=feedback_area)
        generate_style_details_button.click(
            lambda prefix: asyncio.run(generate_style_details(prefix)),
            inputs=[style_prefix_input],
            outputs=style_suffix_input
        )
        
        # Script Analysis
        with gr.Tab("📊 Script Analysis"):
            script_analysis_input = gr.Textbox(label="📜 Script to Analyze", lines=10)
            director_style_input = gr.Dropdown(choices=core.get_director_styles(), label="🎭 Director Style")
            analyze_button = gr.Button("🔍 Analyze Script")
            analysis_output = gr.Textbox(label="📊 Analysis Result")
            
            analyze_button.click(
                lambda *args: asyncio.run(analyze_script(*args)),
                inputs=[script_analysis_input, director_style_input], 
                outputs=analysis_output
            )
        
        # Prompt Logs
        with gr.Tab("📜 Prompt Logs"):
            log_output = gr.JSON(label="📊 Prompt Generation Logs")
            refresh_logs_button = gr.Button("🔄 Refresh Logs")
            
            refresh_logs_button.click(get_prompt_logs, inputs=None, outputs=log_output)

    if __name__ == "__main__":
        app.launch(share=True)
