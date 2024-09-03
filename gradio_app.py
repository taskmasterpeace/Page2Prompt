import gradio as gr
import asyncio
import json
import time
import csv
import pyperclip
from gradio_config import Config
from gradio_prompt_manager import PromptManager
from gradio_styles import StyleManager
from gradio_script_analyzer import ScriptAnalyzer
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import MetaChainException, PromptGenerationError, ScriptAnalysisError
from debug_utils import logger, debug_func, get_error_report
from gradio_core import PromptForgeCore
from gradio_meta_chain import MetaChain

# Initialize components
config = Config()
core = PromptForgeCore()
prompt_manager = PromptManager()
style_manager = StyleManager("styles.csv")
script_analyzer = ScriptAnalyzer()
meta_chain = MetaChain(core)
core.meta_chain = meta_chain
prompt_logger = PromptLogger()
subject_manager = core.subject_manager

# Load subjects
subjects = subject_manager.get_subjects()
subject_names = [s["name"] for s in subjects]

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
def generate_prompt_wrapper(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, camera_shot, camera_move, camera_size, existing_prompts, style_prefix, style_suffix, director_style):
    async def async_generate():
        start_time = time.time()
        try:
            logger.info("Starting generate_prompt_wrapper")

            active_subjects = person_subjects + animal_subjects + place_subjects + thing_subjects + other_subjects
            active_subjects_list = [s for s in subject_manager.get_subjects() if s["name"] in active_subjects]

            def format_camera_work(shot, move, size):
                camera_descriptions = []
                if shot:
                    camera_descriptions.append(f"In a {shot},")
                if move:
                    camera_descriptions.append(f"with a {move},")
                if size:
                    camera_descriptions.append(f"framed as a {size},")
                    
                if camera_descriptions:
                    return " ".join(camera_descriptions) + " we see"
                return ""

            camera_work_description = format_camera_work(camera_shot, camera_move, camera_size)

            meta_chain_start = time.time()
            result = await core.meta_chain.generate_prompt(
                style=style,
                highlighted_text=highlighted_text,
                shot_description=f"{camera_work_description} {shot_description}".strip(),
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
                return "", "", "", json.dumps({"error": f"Unexpected result type {type(result)}"}), "Error: Unexpected result type", json.dumps([])

            def format_prompt(prefix, content, suffix):
                prefix = prefix.strip() if prefix else ""
                suffix = suffix.strip() if suffix else ""
                parts = [part for part in [prefix, content, suffix] if part]
                return " ".join(parts)

            concise = format_prompt(style_prefix, result.get('Concise Prompt', ''), style_suffix)
            normal = format_prompt(style_prefix, result.get('Normal Prompt', ''), style_suffix)
            detailed = format_prompt(style_prefix, result.get('Detailed Prompt', ''), style_suffix)

            logger.info(f"Prompts generated - Concise: {concise[:50]}..., Normal: {normal[:50]}..., Detailed: {detailed[:50]}...")

            structured_json = json.dumps(result, indent=2)
            generation_message = "Prompts generated successfully"
            active_subjects_json = json.dumps(active_subjects_list, indent=2)
                
            return concise, normal, detailed, structured_json, generation_message, active_subjects_json
        except Exception as e:
            logger.exception("Unexpected error in generate_prompt_wrapper")
            error_report = get_error_report()
            error_message = f"Error: {str(e)}"
            return error_message, error_message, error_message, json.dumps({"error": str(e), "error_report": error_report}), error_message, json.dumps([])
        finally:
            logger.info(f"generate_prompt_wrapper took {time.time() - start_time:.2f} seconds total")

    return asyncio.run(async_generate())

def update_style_inputs(style_name):
    style = style_manager.get_style(style_name)
    return gr.update(value=style['prefix']), gr.update(value=style['suffix'])

# Define Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# 🎬 Page 2 Prompt - Bring Your Script to Life")
    
    # Define feedback_area at the beginning
    feedback_area = gr.Textbox(label="💬 Feedback", interactive=False)
    
    with gr.Tabs():
        with gr.TabItem("Script & Prompt Generation"):
            with gr.Row():
                with gr.Column(scale=1):
                    # Left column (Input)
                    with gr.Group():
                        gr.Markdown("## 📝 Shot Details")
                        shot_description_input = gr.Textbox(label="📸 Shot Description", lines=2)
                        directors_notes_input = gr.Textbox(label="🎭 Director's Notes", lines=3)
            
                    with gr.Group():
                        gr.Markdown("## 👥 Subjects")
                        with gr.Row():
                            person_subjects = gr.CheckboxGroup(label="People", choices=[])
                            animal_subjects = gr.CheckboxGroup(label="Animals", choices=[])
                        with gr.Row():
                            place_subjects = gr.CheckboxGroup(label="Places", choices=[])
                            thing_subjects = gr.CheckboxGroup(label="Things", choices=[])
                        with gr.Row():
                            other_subjects = gr.CheckboxGroup(label="Other", choices=[])
            
                    generate_button = gr.Button("🚀 Generate Prompt")
                    
                    with gr.Group():
                        gr.Markdown("## 🎨 Style")
                        with gr.Row():
                            style_input = gr.Dropdown(choices=style_manager.get_style_names(), label="Style", scale=1)
                            style_prefix_input = gr.Textbox(label="Style Prefix", placeholder="Enter style name/details", scale=2)
                            style_suffix_input = gr.Textbox(label="Style Suffix", placeholder="Enter style suffix", scale=2)
                        with gr.Row():
                            save_style_button = gr.Button("💾 Save Style")
                            update_style_button = gr.Button("🔄 Update Style")
                            delete_style_button = gr.Button("🗑️ Delete Style")
                            generate_style_details_button = gr.Button("🔍 Generate Style Details")
                            generate_random_style_button = gr.Button("🎲 Generate Random Style")
                        director_style_input = gr.Dropdown(choices=["Default"] + list(meta_chain.director_styles.keys()), label="🎬 Director's Style")
                
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

                with gr.Column(scale=1):
                    # Right column (Generated Prompts)
                    gr.Markdown("## 🖼️ Generated Prompts")
                    with gr.Group():
                        concise_prompt = gr.Textbox(label="Concise Prompt", lines=5)
                        copy_concise_button = gr.Button("📋 Copy", scale=0.1)
                    with gr.Group():
                        normal_prompt = gr.Textbox(label="Normal Prompt", lines=10)
                        copy_normal_button = gr.Button("📋 Copy", scale=0.1)
                    with gr.Group():
                        detailed_prompt = gr.Textbox(label="Detailed Prompt", lines=15)
                        copy_detailed_button = gr.Button("📋 Copy", scale=0.1)
                    structured_prompt = gr.JSON(label="Structured Prompt")
                    generation_message = gr.Textbox(label="Generation Message")
            
                    with gr.Row():
                        save_button = gr.Button("💾 Save Prompts")
                        copy_all_button = gr.Button("📋 Copy All Prompts")
                        send_button = gr.Button("📤 Send Prompts")
                        clear_button = gr.Button("🧹 Clear All")

            # Add a section to display active subjects
            with gr.Row():
                active_subjects_display = gr.JSON(label="Active Subjects")
            
        with gr.TabItem("Subject Management"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## 👤 Subject Details")
                    subjects_dropdown = gr.Dropdown(label="Select Subject", choices=subject_names, allow_custom_value=True)
                    subject_name = gr.Textbox(label="Subject Name")
                    subject_category = gr.Dropdown(label="Subject Category", choices=["Person", "Animal", "Place", "Thing", "Other"])
                    subject_description = gr.Textbox(label="Subject Description", lines=3)
                    subject_active = gr.Checkbox(label="Active in Scene")
                    subject_hairstyle = gr.Textbox(label="Hairstyle")
                    subject_clothing = gr.Textbox(label="Clothing")
                    subject_body_type = gr.Textbox(label="Body Type")
                    subject_accessories = gr.Textbox(label="Accessories")
                    subject_age = gr.Number(label="Age")
                    subject_height = gr.Textbox(label="Height")
                    subject_distinguishing_features = gr.Textbox(label="Distinguishing Features")
                    subject_scene_order = gr.Number(label="Scene Order")
                
                    with gr.Row():
                        add_subject_button = gr.Button("➕ Add Subject")
                        edit_subject_button = gr.Button("✏️ Update Subject")
                        delete_subject_button = gr.Button("🗑️ Delete Subject")
                
                with gr.Column(scale=1):
                    subjects_list = gr.JSON(label="Added Subjects")
                    
                    with gr.Row():
                        sort_by_scene_order_button = gr.Button("Sort by Scene Order")
                        sort_by_character_button = gr.Button("Sort by Character")

        with gr.TabItem("Shot List"):
            gr.Markdown("## 📋 Shot List")
            shot_list_input = gr.Textbox(label="Enter Shot List (JSON format)", lines=10)
            update_shot_list_button = gr.Button("Update Shot List")
            shot_list_display = gr.JSON(label="Current Shot List")

    # Event handlers and utility functions
    def update_feedback(message):
        return gr.update(value=message)

    def save_style(style_name, prefix, suffix):
        if not style_name:
            return update_feedback("Error: Style name cannot be empty.")
        style_manager.add_style(style_name, prefix, suffix)
        return update_feedback(f"Style '{style_name}' saved successfully.")

    def update_style(style_name, prefix, suffix):
        if not style_name:
            return update_feedback("Error: Style name cannot be empty.")
        style_manager.add_style(style_name, prefix, suffix)
        return update_feedback(f"Style '{style_name}' updated successfully.")

    def delete_style(style_name):
        if not style_name:
            return update_feedback("Error: Style name cannot be empty.")
        style_manager.remove_style(style_name)
        return update_feedback(f"Style '{style_name}' deleted successfully.")

    def add_subject(name, category, description, active, hairstyle, clothing, body_type, accessories, age, height, distinguishing_features, scene_order):
        new_subject = {
            "name": name,
            "category": category,
            "description": description,
            "active": active,
            "hairstyle": hairstyle,
            "clothing": clothing,
            "body_type": body_type,
            "accessories": accessories,
            "age": age,
            "height": height,
            "distinguishing_features": distinguishing_features,
            "scene_order": scene_order
        }
        subject_manager.add_subject(new_subject)
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        return update_result + subject_displays + (update_feedback(f"Subject '{name}' added successfully"),)

    def update_subject(name, category, description, active, hairstyle, clothing, body_type, accessories, age, height, distinguishing_features, scene_order):
        updated_subject = {
            "name": name,
            "category": category,
            "description": description,
            "active": str(active),
            "hairstyle": hairstyle,
            "clothing": clothing,
            "body_type": body_type,
            "accessories": accessories,
            "age": age,
            "height": height,
            "distinguishing_features": distinguishing_features,
            "scene_order": scene_order
        }
        subject_manager.update_subject(updated_subject)
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        return update_result + subject_displays + (update_feedback(f"Subject '{name}' updated successfully"),)

    def toggle_subject_active(subject_name, is_active):
        subject_manager.toggle_subject_active(subject_name, is_active)
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        feedback = update_feedback(f"Subject '{subject_name}' active status updated")

        # Get the subject details
        subject = subject_manager.get_subject_by_name(subject_name)

        # Create a list of 21 outputs, using gr.update() for components that don't need changes
        outputs = [
            gr.update(choices=update_result[0].choices, value=update_result[0].value),  # subjects_dropdown
            gr.update(choices=update_result[1].choices, value=update_result[1].value),  # subjects_dropdown (duplicate)
            gr.update(value=update_result[2]),  # subjects_list
            gr.update(value=subject.get('name', '')),  # subject_name
            gr.update(value=subject.get('category', '')),  # subject_category
            gr.update(value=subject.get('description', '')),  # subject_description
            gr.update(value=is_active),  # subject_active
            gr.update(value=subject.get('hairstyle', '')),  # subject_hairstyle
            gr.update(value=subject.get('clothing', '')),  # subject_clothing
            gr.update(value=subject.get('body_type', '')),  # subject_body_type
            gr.update(value=subject.get('accessories', '')),  # subject_accessories
            gr.update(value=subject.get('age', '')),  # subject_age
            gr.update(value=subject.get('height', '')),  # subject_height
            gr.update(value=subject.get('distinguishing_features', '')),  # subject_distinguishing_features
            gr.update(value=subject.get('scene_order', '')),  # subject_scene_order
            gr.update(choices=subject_displays[0].choices, value=subject_displays[0].value),  # person_subjects
            gr.update(choices=subject_displays[1].choices, value=subject_displays[1].value),  # animal_subjects
            gr.update(choices=subject_displays[2].choices, value=subject_displays[2].value),  # place_subjects
            gr.update(choices=subject_displays[3].choices, value=subject_displays[3].value),  # thing_subjects
            gr.update(choices=subject_displays[4].choices, value=subject_displays[4].value),  # other_subjects
            gr.update(value=feedback)  # feedback_area
        ]
        return outputs

    def delete_subject(name):
        subject_manager.delete_subject(name)
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        return update_result + subject_displays + (update_feedback(f"Subject '{name}' deleted successfully"),)

    def update_subjects_interface():
        subjects = subject_manager.get_subjects()
        subject_names = [s["name"] for s in subjects]
        categories = list(set(s["category"] for s in subjects))
        return (
            gr.update(choices=subject_names, value=None),
            gr.update(choices=subject_names, value=None),
            json.dumps(subjects, indent=2),
            "", gr.update(choices=categories, value=None), "", False, "", "", "", "", "", "", "", "",
            *update_subject_displays()
        )

    def update_subject_displays():
        subjects = subject_manager.get_subjects()
        people = [s["name"] for s in subjects if s["category"] == "Person"]
        animals = [s["name"] for s in subjects if s["category"] == "Animal"]
        places = [s["name"] for s in subjects if s["category"] == "Place"]
        things = [s["name"] for s in subjects if s["category"] == "Thing"]
        others = [s["name"] for s in subjects if s["category"] == "Other"]
    
        active_subjects = subject_manager.get_active_subjects()
        active_names = [s["name"] for s in active_subjects]
    
        return (
            gr.update(choices=people, value=[name for name in active_names if name in people]),
            gr.update(choices=animals, value=[name for name in active_names if name in animals]),
            gr.update(choices=places, value=[name for name in active_names if name in places]),
            gr.update(choices=things, value=[name for name in active_names if name in things]),
            gr.update(choices=others, value=[name for name in active_names if name in others])
        )

    def toggle_subject_active(subject_name, is_active):
        subject_manager.toggle_subject_active(subject_name, is_active)
        return update_subject_displays()

    def update_subject_active_status(*active_subjects):
        all_active = []
        for subject_group in active_subjects:
            if isinstance(subject_group, list):
                all_active.extend(subject_group)
        for subject in subject_manager.get_subjects():
            subject_manager.toggle_subject_active(subject["name"], subject["name"] in all_active)
        return update_subject_displays()

    def load_subject(name):
        subject = subject_manager.get_subject_by_name(name)
        if subject:
            return (
                subject["name"],
                subject["category"],
                subject["description"],
                subject["active"] == 'True',
                subject.get("hairstyle", ""),
                subject.get("clothing", ""),
                subject.get("body_type", ""),
                subject.get("accessories", ""),
                subject.get("age", ""),
                subject.get("height", ""),
                subject.get("distinguishing_features", ""),
                subject.get("scene_order", ""),
                update_feedback(f"Loaded subject: {name}")
            )
        return "", "", "", False, "", "", "", "", "", "", "", "", update_feedback("Subject not found")

    def sort_subjects_by_scene_order():
        sorted_subjects = subject_manager.get_subjects_by_scene_order()
        return json.dumps(sorted_subjects, indent=2)

    def sort_subjects_by_character():
        sorted_subjects = subject_manager.get_subjects_by_character()
        return json.dumps(sorted_subjects, indent=2)

    def update_shot_list(shot_list_json):
        try:
            shot_list = json.loads(shot_list_json)
            # Here you would typically update your shot list in your backend
            # For now, we'll just echo it back
            return json.dumps(shot_list, indent=2), update_feedback("Shot list updated successfully")
        except json.JSONDecodeError:
            return "", update_feedback("Error: Invalid JSON format")

    # Connect event handlers
    save_style_button.click(save_style, inputs=[style_input, style_prefix_input, style_suffix_input], outputs=[feedback_area])
    update_style_button.click(update_style, inputs=[style_input, style_prefix_input, style_suffix_input], outputs=[feedback_area])
    delete_style_button.click(delete_style, inputs=[style_input], outputs=[feedback_area])

    # Add these functions to handle copying and sending prompts
    def copy_prompt(prompt):
        pyperclip.copy(prompt)
        return update_feedback("Prompt copied to clipboard")

    def copy_all_prompts(concise, normal, detailed):
        all_prompts = f"Concise Prompt:\n{concise}\n\nNormal Prompt:\n{normal}\n\nDetailed Prompt:\n{detailed}"
        pyperclip.copy(all_prompts)
        return update_feedback("All prompts copied to clipboard")

    def send_prompts(concise, normal, detailed):
        # Placeholder function - implement actual sending logic in the future
        return update_feedback("Prompts sent successfully")

    # Connect the new buttons to their respective functions
    copy_concise_button.click(copy_prompt, inputs=[concise_prompt], outputs=[feedback_area])
    copy_normal_button.click(copy_prompt, inputs=[normal_prompt], outputs=[feedback_area])
    copy_detailed_button.click(copy_prompt, inputs=[detailed_prompt], outputs=[feedback_area])
    copy_all_button.click(copy_all_prompts, inputs=[concise_prompt, normal_prompt, detailed_prompt], outputs=[feedback_area])
    send_button.click(send_prompts, inputs=[concise_prompt, normal_prompt, detailed_prompt], outputs=[feedback_area])

    generate_button.click(
        generate_prompt_wrapper,
        inputs=[style_input, highlighted_text_input, shot_description_input,
                directors_notes_input, script_input, stick_to_script_input,
                end_parameters_input, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects,
                camera_shot_input, camera_move_input, camera_size_input, 
                concise_prompt, style_prefix_input, style_suffix_input, director_style_input],
        outputs=[concise_prompt, normal_prompt, detailed_prompt, structured_prompt, generation_message, active_subjects_display]
    )

    add_subject_button.click(
        add_subject,
        inputs=[subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order],
        outputs=[subjects_dropdown, subjects_dropdown, subjects_list, subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
    )

    edit_subject_button.click(
        update_subject,
        inputs=[subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order],
        outputs=[subjects_dropdown, subjects_dropdown, subjects_list, subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
    )

    subject_active.change(
        toggle_subject_active,
        inputs=[subjects_dropdown, subject_active],
        outputs=[
            subjects_dropdown, subjects_dropdown, subjects_list, 
            subject_name, subject_category, subject_description, subject_active, 
            subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, 
            subject_age, subject_height, subject_distinguishing_features, subject_scene_order, 
            person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, 
            feedback_area
        ]
    )

    delete_subject_button.click(
        delete_subject,
        inputs=[subjects_dropdown],
        outputs=[subjects_dropdown, subjects_dropdown, subjects_list, subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
    )

    # Add this new event handler for toggling subject active status
    for subject_group in [person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects]:
        subject_group.change(
            update_subject_active_status,
            inputs=[person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects],
            outputs=[person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects]
        )

    # Add individual event handlers for each subject checkbox
    def create_toggle_handler(category):
        def handler(subject_names):
            for subject_name in subject_names:
                subject_manager.toggle_subject_active(subject_name, True)
            for subject in subject_manager.get_subjects():
                if subject['category'] == category and subject['name'] not in subject_names:
                    subject_manager.toggle_subject_active(subject['name'], False)
            
            update_result = update_subjects_interface()
            subject_displays = update_subject_displays()
            feedback = update_feedback(f"Subjects in {category} category updated")
            
            # Create a list of 21 outputs, using gr.update() for components that don't need changes
            outputs = [
                update_result[0],  # subjects_dropdown
                update_result[1],  # subjects_dropdown (duplicate)
                update_result[2],  # subjects_list
                gr.update(),  # subject_name
                gr.update(),  # subject_category
                gr.update(),  # subject_description
                gr.update(),  # subject_active
                gr.update(),  # subject_hairstyle
                gr.update(),  # subject_clothing
                gr.update(),  # subject_body_type
                gr.update(),  # subject_accessories
                gr.update(),  # subject_age
                gr.update(),  # subject_height
                gr.update(),  # subject_distinguishing_features
                gr.update(),  # subject_scene_order
                subject_displays[0],  # person_subjects
                subject_displays[1],  # animal_subjects
                subject_displays[2],  # place_subjects
                subject_displays[3],  # thing_subjects
                subject_displays[4],  # other_subjects
                feedback  # feedback_area
            ]
            return outputs
        return handler

    for subject_group in [person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects]:
        subject_group.change(
            toggle_subject_active,
            inputs=[subjects_dropdown, subject_active],
            outputs=[subjects_dropdown, subjects_dropdown, subjects_list, subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
        )

    def create_toggle_handler(category):
        def handler(subject_names):
            for subject_name in subject_names:
                subject_manager.toggle_subject_active(subject_name, True)
            for subject in subject_manager.get_subjects():
                if subject['category'] == category and subject['name'] not in subject_names:
                    subject_manager.toggle_subject_active(subject['name'], False)
            
            update_result = update_subjects_interface()
            subject_displays = update_subject_displays()
            feedback = update_feedback(f"Subjects in {category} category updated")
            
            # Create a list of 21 outputs, using gr.update() for components that don't need changes
            outputs = [
                update_result[0],  # subjects_dropdown
                update_result[1],  # subjects_dropdown (duplicate)
                update_result[2],  # subjects_list
                gr.update(),  # subject_name
                gr.update(),  # subject_category
                gr.update(),  # subject_description
                gr.update(),  # subject_active
                gr.update(),  # subject_hairstyle
                gr.update(),  # subject_clothing
                gr.update(),  # subject_body_type
                gr.update(),  # subject_accessories
                gr.update(),  # subject_age
                gr.update(),  # subject_height
                gr.update(),  # subject_distinguishing_features
                gr.update(),  # subject_scene_order
                subject_displays[0],  # person_subjects
                subject_displays[1],  # animal_subjects
                subject_displays[2],  # place_subjects
                subject_displays[3],  # thing_subjects
                subject_displays[4],  # other_subjects
                feedback  # feedback_area
            ]
            return outputs
        return handler

    subjects_dropdown.change(
        load_subject,
        inputs=[subjects_dropdown],
        outputs=[subject_name, subject_category, subject_description, subject_active, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, feedback_area]
    )

    sort_by_scene_order_button.click(sort_subjects_by_scene_order, outputs=[subjects_list])
    sort_by_character_button.click(sort_subjects_by_character, outputs=[subjects_list])

    update_shot_list_button.click(
        update_shot_list,
        inputs=[shot_list_input],
        outputs=[shot_list_display, feedback_area]
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

if __name__ == "__main__":
    app.launch()
