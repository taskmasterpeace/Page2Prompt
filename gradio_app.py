import gradio as gr
import asyncio
import json
import time
import csv
import pyperclip
import pandas as pd
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
core.set_meta_chain(meta_chain)
prompt_logger = PromptLogger()
subject_manager = core.subject_manager

# Load subjects
subjects = subject_manager.get_subjects()
subject_names = [s["name"] for s in subjects]
if not subject_names:
    subject_names = ["No subjects available"]

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
def generate_prompt_wrapper(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, shot_type, camera_angle, camera_movement, framing, depth_of_field, existing_prompts, style_prefix, style_suffix, director_style):
    async def async_generate():
        start_time = time.time()
        try:
            logger.info("Starting generate_prompt_wrapper")

            active_subjects = person_subjects + animal_subjects + place_subjects + thing_subjects + other_subjects
            active_subjects_list = subject_manager.get_active_subjects()

            def format_camera_work(shot_type, camera_angle, camera_movement, framing, depth_of_field):
                camera_descriptions = []
                if shot_type and shot_type != "AI Suggest":
                    camera_descriptions.append(f"Using a {shot_type},")
                if camera_angle and camera_angle != "AI Suggest":
                    camera_descriptions.append(f"with a {camera_angle} angle,")
                if camera_movement and camera_movement != "AI Suggest":
                    camera_descriptions.append(f"using {camera_movement},")
                if framing and framing != "AI Suggest":
                    camera_descriptions.append(f"framed with {framing},")
                if depth_of_field and depth_of_field != "AI Suggest":
                    camera_descriptions.append(f"with {depth_of_field},")
                
                if camera_descriptions:
                    return " ".join(camera_descriptions) + " we see"
                return ""

            camera_work_description = format_camera_work(shot_type, camera_angle, camera_movement, framing, depth_of_field)

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
                camera_shot=shot_type,
                camera_move=camera_movement,
                camera_size=camera_angle
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
                            person_subjects = gr.CheckboxGroup(label="People", choices=subject_manager.get_subjects_by_category("Person"))
                            animal_subjects = gr.CheckboxGroup(label="Animals", choices=subject_manager.get_subjects_by_category("Animal"))
                        with gr.Row():
                            place_subjects = gr.CheckboxGroup(label="Places", choices=subject_manager.get_subjects_by_category("Place"))
                            thing_subjects = gr.CheckboxGroup(label="Things", choices=subject_manager.get_subjects_by_category("Thing"))
                        with gr.Row():
                            other_subjects = gr.CheckboxGroup(label="Other", choices=subject_manager.get_subjects_by_category("Other"))
            
                    # Add this line to create a dropdown with all subject names
                    all_subjects_dropdown = gr.Dropdown(label="All Subjects", choices=subject_manager.get_all_subject_names(), multiselect=True)
            
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

                            async def generate_style_details(prefix):
                                return await meta_chain.generate_style_suffix(prefix)

                            async def generate_random_style():
                                random_prefix = "A random artistic style"  # You can make this more sophisticated
                                suffix = await meta_chain.generate_style_suffix(random_prefix)
                                return random_prefix, suffix

                            generate_style_details_button.click(
                                generate_style_details,
                                inputs=[style_prefix_input],
                                outputs=[style_suffix_input]
                            )

                            generate_random_style_button.click(
                                generate_random_style,
                                outputs=[style_prefix_input, style_suffix_input]
                            )
                        director_style_input = gr.Dropdown(choices=["Default"] + list(meta_chain.director_styles.keys()), label="🎬 Director's Style")
                
                    style_input.change(
                        update_style_inputs,
                        inputs=[style_input],
                        outputs=[style_prefix_input, style_suffix_input]
                    )
                    
                    script_input = gr.Textbox(label="📜 Script", lines=10)
                    stick_to_script_input = gr.Checkbox(label="📌 Stick to Script")
                    highlighted_text_input = gr.Textbox(label="🖍️ Highlighted Text", lines=3)
                    
                    from gradio_shot_library import get_all_options, get_description

                    with gr.Group():
                        gr.Markdown("## 📷 Shot Configuration")
                        shot_options = get_all_options()
    
                        with gr.Row():
                            shot_type = gr.Dropdown(label="Shot Type", choices=["AI Suggest"] + shot_options["Shot Types"])
                            camera_angle = gr.Dropdown(label="Camera Angle", choices=["AI Suggest"] + shot_options["Camera Angles"])
    
                        with gr.Row():
                            camera_movement = gr.Dropdown(label="Camera Movement", choices=["AI Suggest"] + shot_options["Camera Movements"])
                            framing = gr.Dropdown(label="Framing", choices=["AI Suggest"] + shot_options["Framing"])
    
                        with gr.Row():
                            depth_of_field = gr.Dropdown(label="Depth of Field", choices=["AI Suggest"] + shot_options["Depth of Field"])
        
                        shot_description = gr.Textbox(label="Shot Description", lines=3, interactive=False)
    
                        def update_shot_description(*args):
                            categories = ["Shot Types", "Camera Angles", "Camera Movements", "Framing", "Depth of Field"]
                            description = ""
                            for category, value in zip(categories, args):
                                if value != "AI Suggest":
                                    description += f"{category}: {value} - {get_description(category, value)}\n"
                            return description if description else "Select options to see the shot description."

                        for component in [shot_type, camera_angle, camera_movement, framing, depth_of_field]:
                            component.change(
                                update_shot_description,
                                inputs=[shot_type, camera_angle, camera_movement, framing, depth_of_field],
                                outputs=[shot_description]
                            )
                    
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
                    # Removed the subject_active checkbox
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
                        delete_subject_button = gr.Button("🗑️ Delete Subject", elem_id="delete_subject_button")
                
                with gr.Column(scale=1):
                    subjects_list = gr.JSON(label="Added Subjects")
                    
                    with gr.Row():
                        sort_by_scene_order_button = gr.Button("Sort by Scene Order")
                        sort_by_character_button = gr.Button("Sort by Character")

        with gr.TabItem("Shot List"):
            gr.Markdown("## 📋 Shot List")
            with gr.Row():
                script_input_for_shot_list = gr.Textbox(label="Script for Shot List", lines=10)
                director_style_for_shot_list = gr.Dropdown(label="Director's Style", choices=core.get_director_styles())

            generate_shot_list_button = gr.Button("Generate Shot List")

            shot_list_display = gr.DataFrame(
                headers=["Scene", "Shot", "Script Content", "Shot Description", "Characters", "Camera Work", "Shot Type", "Completed"],
                datatype=["number", "number", "str", "str", "str", "str", "str", "bool"],
                label="Shot List",
                interactive=True
            )

            with gr.Row():
                export_shot_list_button = gr.Button("Export Shot List")
                import_shot_list_button = gr.UploadButton("Import Shot List", file_types=["csv", "json"])
    
            selected_shot_description = gr.Textbox(label="Selected Shot Description", lines=3)
            transfer_to_prompt_button = gr.Button("Transfer to Prompt Generation")

            with gr.Row():
                add_shot_button = gr.Button("Add Shot")
                delete_shot_button = gr.Button("Delete Selected Shot")
                move_up_button = gr.Button("Move Shot Up")
                move_down_button = gr.Button("Move Shot Down")

            with gr.Row():
                scene_input = gr.Number(label="Scene")
                shot_input = gr.Number(label="Shot")
                script_content_input = gr.Textbox(label="Script Content", lines=2)
                shot_description_input = gr.Textbox(label="Shot Description", lines=2)
                characters_input = gr.Textbox(label="Characters")
                camera_work_input = gr.Textbox(label="Camera Work")
                shot_type_input = gr.Textbox(label="Shot Type")

        # Remove the duplicate "Script & Prompt Generation" tab

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

    def add_subject(name, category, description, hairstyle, clothing, body_type, accessories, age, height, distinguishing_features, scene_order):
        try:
            new_subject = {
                "name": name,
                "category": category,
                "description": description,
                "active": "False",  # Set to False by default
                "hairstyle": hairstyle,
                "clothing": clothing,
                "body_type": body_type,
                "accessories": accessories,
                "age": age,
                "height": height,
                "distinguishing_features": distinguishing_features,
                "scene_order": scene_order
            }
            success, message = subject_manager.add_subject(new_subject)
            if success:
                return refresh_all_subject_components() + (gr.update(value=message),)
            else:
                return [gr.update() for _ in range(19)] + [gr.update(value=message)]
        except Exception as e:
            error_message = f"Error adding subject: {str(e)}"
            logger.exception(error_message)
            return [gr.update() for _ in range(19)] + [gr.update(value=error_message)]

    def refresh_all_subject_components():
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        all_subjects_list = gr.update(choices=subject_manager.get_all_subject_names())
        return update_result + subject_displays + (all_subjects_list, update_feedback("Subject added and all components refreshed"),)

    def update_subject(name, category, description, hairstyle, clothing, body_type, accessories, age, height, distinguishing_features, scene_order):
        try:
            updated_subject = {
                "name": name,
                "category": category,
                "description": description,
                "hairstyle": hairstyle,
                "clothing": clothing,
                "body_type": body_type,
                "accessories": accessories,
                "age": str(age) if age is not None else "",  # Convert age to string
                "height": height,
                "distinguishing_features": distinguishing_features,
                "scene_order": str(scene_order) if scene_order is not None else ""  # Convert scene_order to string
            }
            subject_manager.update_subject(updated_subject)
            update_result = update_subjects_interface()
            subject_displays = update_subject_displays()
            feedback = update_feedback(f"Subject '{name}' updated successfully")
            return update_result + subject_displays + (feedback,)
        except Exception as e:
            logger.exception(f"Error updating subject: {str(e)}")
            error_feedback = update_feedback(f"Error updating subject: {str(e)}")
            return [gr.update() for _ in range(19)] + [error_feedback]

    def toggle_subject_active(subject_name, is_active):
        subject_manager.toggle_subject_active(subject_name, is_active)
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        feedback = update_feedback(f"Subject '{subject_name}' active status updated")

        # Get the subject details
        subject = subject_manager.get_subject_by_name(subject_name)

        # Create a list of 21 outputs, using gr.update() for components that don't need changes
        outputs = [
            update_result[0],  # subjects_dropdown
            update_result[1],  # subjects_dropdown (duplicate)
            gr.update(value=update_result[2]),  # subjects_list
            gr.update(value=subject.get('name', '') if subject else ''),  # subject_name
            gr.update(value=subject.get('category', '') if subject else ''),  # subject_category
            gr.update(value=subject.get('description', '') if subject else ''),  # subject_description
            gr.update(value=is_active),  # subject_active
            gr.update(value=subject.get('hairstyle', '') if subject else ''),  # subject_hairstyle
            gr.update(value=subject.get('clothing', '') if subject else ''),  # subject_clothing
            gr.update(value=subject.get('body_type', '') if subject else ''),  # subject_body_type
            gr.update(value=subject.get('accessories', '') if subject else ''),  # subject_accessories
            gr.update(value=subject.get('age', '') if subject else ''),  # subject_age
            gr.update(value=subject.get('height', '') if subject else ''),  # subject_height
            gr.update(value=subject.get('distinguishing_features', '') if subject else ''),  # subject_distinguishing_features
            gr.update(value=subject.get('scene_order', '') if subject else ''),  # subject_scene_order
            subject_displays[0],  # person_subjects
            subject_displays[1],  # animal_subjects
            subject_displays[2],  # place_subjects
            subject_displays[3],  # thing_subjects
            subject_displays[4],  # other_subjects
            gr.update(value=feedback)  # feedback_area
        ]
        return outputs

    def delete_subject(name):
        try:
            subject_manager.delete_subject(name)
            update_result = update_subjects_interface()
            subject_displays = update_subject_displays()
            all_subjects_list = gr.update(choices=subject_manager.get_all_subject_names())
            feedback = update_feedback(f"Subject '{name}' deleted successfully")
        
            # Create a list of outputs for all components that need updating
            outputs = [
                update_result[0],  # subjects_dropdown
                update_result[1],  # subjects_dropdown (duplicate)
                gr.update(value=update_result[2]),  # subjects_list
                gr.update(value=""),  # subject_name
                gr.update(value=""),  # subject_category
                gr.update(value=""),  # subject_description
                gr.update(value=False),  # subject_active
                gr.update(value=""),  # subject_hairstyle
                gr.update(value=""),  # subject_clothing
                gr.update(value=""),  # subject_body_type
                gr.update(value=""),  # subject_accessories
                gr.update(value=""),  # subject_age
                gr.update(value=""),  # subject_height
                gr.update(value=""),  # subject_distinguishing_features
                gr.update(value=""),  # subject_scene_order
                subject_displays[0],  # person_subjects
                subject_displays[1],  # animal_subjects
                subject_displays[2],  # place_subjects
                subject_displays[3],  # thing_subjects
                subject_displays[4],  # other_subjects
                all_subjects_list,  # all_subjects_dropdown
                feedback  # feedback_area
            ]
            return outputs
        except Exception as e:
            error_message = f"Error deleting subject '{name}': {str(e)}"
            logger.error(error_message)
            return [gr.update() for _ in range(21)] + [gr.update(value=error_message)]

    def update_subjects_interface():
        subjects = subject_manager.get_subjects()
        subject_names = [s["name"] for s in subjects]
        categories = list(set(s["category"] for s in subjects))
        active_subjects = subject_manager.get_active_subjects()
        return (
            gr.update(choices=subject_names, value=None),
            gr.update(choices=subject_names, value=None),
            json.dumps(subjects, indent=2),
            "", gr.update(choices=categories), "", False, "", "", "", "", "", "", "", "",
            gr.update(choices=subject_manager.get_subjects_by_category("Person"), value=[s["name"] for s in active_subjects if s["category"] == "Person"]),
            gr.update(choices=subject_manager.get_subjects_by_category("Animal"), value=[s["name"] for s in active_subjects if s["category"] == "Animal"]),
            gr.update(choices=subject_manager.get_subjects_by_category("Place"), value=[s["name"] for s in active_subjects if s["category"] == "Place"]),
            gr.update(choices=subject_manager.get_subjects_by_category("Thing"), value=[s["name"] for s in active_subjects if s["category"] == "Thing"]),
            gr.update(choices=subject_manager.get_subjects_by_category("Other"), value=[s["name"] for s in active_subjects if s["category"] == "Other"])
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
        subject_manager.save_subjects()  # Save the changes to the CSV file
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        feedback = update_feedback(f"Subject '{subject_name}' active status updated")

        return subject_displays + (feedback,)

    def update_subject_active_status(*active_subjects):
        all_active = set()
        for subject_group in active_subjects:
            if isinstance(subject_group, list):
                all_active.update(subject_group)
    
        for subject in subject_manager.get_subjects():
            is_active = subject["name"] in all_active
            subject_manager.toggle_subject_active(subject["name"], is_active)
    
        subject_manager.save_subjects()  # Save the changes to the CSV file
        subject_displays = update_subject_displays()
        active_subjects_json = json.dumps(subject_manager.get_active_subjects(), indent=2)
        feedback = update_feedback("Subject active status updated")
    
        return subject_displays + (gr.update(value=active_subjects_json), feedback)

    def toggle_subject_active(subject_name, is_active):
        subject_manager.toggle_subject_active(subject_name, is_active)
        subject_manager.save_subjects()  # Save the changes to the CSV file
        update_result = update_subjects_interface()
        subject_displays = update_subject_displays()
        feedback = update_feedback(f"Subject '{subject_name}' active status updated")

        # Get the subject details
        subject = subject_manager.get_subject_by_name(subject_name)

        # Create a list of outputs, using gr.update() for components that don't need changes
        outputs = [
            update_result[0],  # subjects_dropdown
            update_result[1],  # subjects_dropdown (duplicate)
            gr.update(value=update_result[2]),  # subjects_list
            gr.update(value=subject.get('name', '') if subject else ''),  # subject_name
            gr.update(value=subject.get('category', '') if subject else ''),  # subject_category
            gr.update(value=subject.get('description', '') if subject else ''),  # subject_description
            gr.update(value=subject.get('hairstyle', '') if subject else ''),  # subject_hairstyle
            gr.update(value=subject.get('clothing', '') if subject else ''),  # subject_clothing
            gr.update(value=subject.get('body_type', '') if subject else ''),  # subject_body_type
            gr.update(value=subject.get('accessories', '') if subject else ''),  # subject_accessories
            gr.update(value=subject.get('age', '') if subject else ''),  # subject_age
            gr.update(value=subject.get('height', '') if subject else ''),  # subject_height
            gr.update(value=subject.get('distinguishing_features', '') if subject else ''),  # subject_distinguishing_features
            gr.update(value=subject.get('scene_order', '') if subject else ''),  # subject_scene_order
            subject_displays[0],  # person_subjects
            subject_displays[1],  # animal_subjects
            subject_displays[2],  # place_subjects
            subject_displays[3],  # thing_subjects
            subject_displays[4],  # other_subjects
            gr.update(value=feedback)  # feedback_area
        ]
        return outputs

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

    async def generate_shot_list(script, director_style, shot_type, camera_angle, camera_movement, framing, depth_of_field):
        try:
            logger.info(f"Generating shot list for director style: {director_style}")
            logger.debug(f"Script content: {script[:100]}...")  # Log first 100 characters of script

            shot_list = await core.analyze_script(script, director_style)
            logger.info(f"Generated shot list: {shot_list}")  # Log the entire shot list for debugging

            if not isinstance(shot_list, dict) or 'shots' not in shot_list:
                raise ValueError("Invalid shot list structure")

            shots = shot_list['shots']
            if not shots:
                raise ValueError("Empty shot list generated")

            # Incorporate user-selected shot configuration
            for shot in shots:
                if shot_type != "AI Suggest":
                    shot['Shot Type'] = shot_type
                camera_work = []
                if camera_angle != "AI Suggest":
                    camera_work.append(camera_angle)
                if camera_movement != "AI Suggest":
                    camera_work.append(camera_movement)
                if framing != "AI Suggest":
                    camera_work.append(framing)
                if depth_of_field != "AI Suggest":
                    camera_work.append(depth_of_field)
                if camera_work:
                    shot['Camera Work'] = ', '.join(filter(None, camera_work))
                elif 'Camera Work' not in shot:
                    shot['Camera Work'] = 'Not specified'

            # Create DataFrame
            df = pd.DataFrame(shots)
            logger.debug(f"DataFrame columns: {df.columns}")

            # Ensure all required columns are present
            required_columns = ["Scene", "Shot", "Script Content", "Shot Description", "Characters", "Camera Work", "Shot Type", "Completed"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = "Not specified"

            # Reorder columns
            df = df[required_columns]

            logger.info(f"Final DataFrame: {df.to_string()}")  # Log the final DataFrame

            return df, update_feedback("Shot list generated successfully")
        except Exception as e:
            logger.exception("Error in generate_shot_list function")
            return None, update_feedback(f"Error generating shot list: {str(e)}")

    def export_shot_list(shot_list):
        try:
            # Export to CSV
            csv_filename = f'shot_list_{int(time.time())}.csv'
            shot_list.to_csv(csv_filename, index=False)
        
            # Export to JSON
            json_filename = f'shot_list_{int(time.time())}.json'
            shot_list.to_json(json_filename, orient='records', indent=2)
    
            return gr.File.update(value=[csv_filename, json_filename], visible=True), update_feedback("Shot list exported successfully as CSV and JSON")
        except Exception as e:
            logger.exception("Error in export_shot_list function")
            return None, update_feedback(f"Error exporting shot list: {str(e)}")

    def transfer_to_prompt_generation(selected_row):
        if selected_row is not None and len(selected_row) > 0:
            shot_description = selected_row.iloc[0]['Shot Description']
            return gr.update(value=shot_description), update_feedback("Shot description transferred to prompt generation")
        else:
            return gr.update(), update_feedback("No row selected. Please select a row from the shot list.")

    def import_shot_list(file):
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file.name)
            elif file.name.endswith('.json'):
                df = pd.read_json(file.name)
            else:
                return None, update_feedback("Unsupported file format. Please use CSV or JSON.")
            return df, update_feedback("Shot list imported successfully")
        except Exception as e:
            return None, update_feedback(f"Error importing shot list: {str(e)}")

    def update_shot_list(shot_list):
        return shot_list, update_feedback("Shot list updated successfully")

    def add_shot(shot_list, scene, shot, script_content, shot_description, characters, camera_work, shot_type):
        new_row = pd.DataFrame({
            'Scene': [scene],
            'Shot': [shot],
            'Script Content': [script_content],
            'Shot Description': [shot_description],
            'Characters': [characters],
            'Camera Work': [camera_work],
            'Shot Type': [shot_type],
            'Completed': [False]
        })
        updated_shot_list = pd.concat([shot_list, new_row], ignore_index=True)
        return updated_shot_list, update_feedback("New shot added successfully")

    def delete_selected_shot(shot_list):
        if shot_list is not None and not shot_list.empty:
            selected_indices = shot_list.index[shot_list['Selected'] == True].tolist()
            if selected_indices:
                updated_shot_list = shot_list.drop(selected_indices).reset_index(drop=True)
                return updated_shot_list, update_feedback("Selected shot(s) deleted successfully")
            else:
                return shot_list, update_feedback("No shot selected for deletion")
        else:
            return shot_list, update_feedback("Shot list is empty or not initialized")

    def move_shot(shot_list, direction):
        if shot_list is not None and not shot_list.empty:
            selected_indices = shot_list.index[shot_list['Selected'] == True].tolist()
            if selected_indices:
                selected_index = selected_indices[0]
                if direction == "up" and selected_index > 0:
                    shot_list.iloc[selected_index-1:selected_index+1] = shot_list.iloc[selected_index-1:selected_index+1].iloc[::-1].values
                elif direction == "down" and selected_index < len(shot_list) - 1:
                    shot_list.iloc[selected_index:selected_index+2] = shot_list.iloc[selected_index:selected_index+2].iloc[::-1].values
                return shot_list.reset_index(drop=True), update_feedback(f"Shot moved {direction} successfully")
            else:
                return shot_list, update_feedback("No shot selected for moving")
        else:
            return shot_list, update_feedback("Shot list is empty or not initialized")

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
                shot_type, camera_angle, camera_movement, framing, depth_of_field,
                concise_prompt, style_prefix_input, style_suffix_input, director_style_input],
        outputs=[concise_prompt, normal_prompt, detailed_prompt, structured_prompt, generation_message, active_subjects_display]
    )

    add_subject_button.click(
        add_subject,
        inputs=[subject_name, subject_category, subject_description, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order],
        outputs=[subjects_dropdown, subjects_dropdown, subjects_list, subject_name, subject_category, subject_description, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
    )

    edit_subject_button.click(
        update_subject,
        inputs=[subject_name, subject_category, subject_description, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order],
        outputs=[subjects_dropdown, subjects_dropdown, subjects_list, subject_name, subject_category, subject_description, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
    )

    all_subjects_dropdown.change(
        update_subject_active_status,
        inputs=[all_subjects_dropdown],
        outputs=[person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, feedback_area]
    )

    delete_subject_button.click(
        delete_subject,
        inputs=[subjects_dropdown],
        outputs=[
            subjects_dropdown, subjects_dropdown, subjects_list, 
            subject_name, subject_category, subject_description,
            subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, 
            subject_age, subject_height, subject_distinguishing_features, subject_scene_order, 
            person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, 
            all_subjects_dropdown, feedback_area
        ]
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
            for subject in subject_manager.get_subjects():
                if subject['category'] == category:
                    subject_manager.toggle_subject_active(subject['name'], subject['name'] in subject_names)
        
            update_result = update_subjects_interface()
            feedback = update_feedback(f"Subjects in {category} category updated")
        
            # Create a list of outputs, using gr.update() for components that don't need changes
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
                gr.update(value=update_result[15]),  # person_subjects
                gr.update(value=update_result[16]),  # animal_subjects
                gr.update(value=update_result[17]),  # place_subjects
                gr.update(value=update_result[18]),  # thing_subjects
                gr.update(value=update_result[19]),  # other_subjects
                feedback  # feedback_area
            ]
            return outputs
        return handler

    for subject_group in [person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects]:
        subject_group.change(
            update_subject_active_status,
            inputs=[person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects],
            outputs=[person_subjects, animal_subjects, place_subjects, thing_subjects, other_subjects, active_subjects_display, feedback_area]
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
        outputs=[subject_name, subject_category, subject_description, subject_hairstyle, subject_clothing, subject_body_type, subject_accessories, subject_age, subject_height, subject_distinguishing_features, subject_scene_order, feedback_area]
    )

    sort_by_scene_order_button.click(sort_subjects_by_scene_order, outputs=[subjects_list])
    sort_by_character_button.click(sort_subjects_by_character, outputs=[subjects_list])

    generate_shot_list_button.click(
        generate_shot_list,
        inputs=[script_input_for_shot_list, director_style_for_shot_list, shot_type, camera_angle, camera_movement, framing, depth_of_field],
        outputs=[shot_list_display, feedback_area]
    )

    export_shot_list_button.click(
        export_shot_list,
        inputs=[shot_list_display],
        outputs=[gr.File(label="Download Files", file_count="multiple"), feedback_area]
    )

    import_shot_list_button.upload(
        import_shot_list,
        inputs=[import_shot_list_button],
        outputs=[shot_list_display, feedback_area]
    )

    shot_list_display.change(
        update_shot_list,
        inputs=[shot_list_display],
        outputs=[shot_list_display, feedback_area]
    )

    transfer_to_prompt_button.click(
        transfer_to_prompt_generation,
        inputs=[shot_list_display],
        outputs=[shot_description_input, feedback_area]
    )

    add_shot_button.click(
        add_shot,
        inputs=[shot_list_display, scene_input, shot_input, script_content_input, shot_description_input, characters_input, camera_work_input, shot_type_input],
        outputs=[shot_list_display, feedback_area]
    )

    delete_shot_button.click(
        delete_selected_shot,
        inputs=[shot_list_display],
        outputs=[shot_list_display, feedback_area]
    )

    move_up_button.click(
        move_shot,
        inputs=[shot_list_display, gr.Textbox(value="up", visible=False)],
        outputs=[shot_list_display, feedback_area]
    )

    move_down_button.click(
        move_shot,
        inputs=[shot_list_display, gr.Textbox(value="down", visible=False)],
        outputs=[shot_list_display, feedback_area]
    )

    # Debug information section
    with gr.Accordion("🐛 Debug Information", open=False):
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
    print("Loaded subjects:", subject_names)
    app.launch()

    # Add this block at the end of the file
    if __name__ == "__main__":
        app.load(
            js="""
            function addDeleteConfirmation() {
                const deleteButton = document.getElementById('delete_subject_button');
                if (deleteButton) {
                    deleteButton.addEventListener('click', function(event) {
                        if (!confirm('Are you sure you want to delete this subject?')) {
                            event.preventDefault();
                            event.stopPropagation();
                        }
                    });
                }
            }
            document.addEventListener('DOMContentLoaded', addDeleteConfirmation);
            """
        )
    def update_active_subjects(selected_subjects):
        for subject in subject_manager.get_subjects():
            subject_manager.toggle_subject_active(subject["name"], subject["name"] in selected_subjects)
        subject_manager.save_subjects()
        subject_displays = update_subject_displays()
        feedback = update_feedback("Active subjects updated")
        return subject_displays + (feedback,)
import os
import time

def save_debug_output(content, filename="debug_output.txt"):
    debug_dir = "debug_logs"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    with open(os.path.join(debug_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Debug output saved to {filename}")
    def transfer_to_prompt_generation(selected_row):
        if selected_row is not None and len(selected_row) > 0:
            shot_description = selected_row.iloc[0]['Shot Description']
            return gr.update(value=shot_description), update_feedback("Shot description transferred to prompt generation")
        else:
            return gr.update(), update_feedback("No row selected. Please select a row from the shot list.")
