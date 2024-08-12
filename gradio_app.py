import gradio as gr
import asyncio
import json
from gradio_core import PromptForgeCore
from gradio_config import Config
from gradio_prompt_manager import PromptManager
from gradio_styles import StyleManager
from gradio_script_analyzer import ScriptAnalyzer
from gradio_meta_chain import MetaChain
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import MetaChainException, PromptGenerationError, ScriptAnalysisError
from debug_utils import logger, debug_func, get_error_report

# Define predictability settings
PREDICTABILITY_SETTINGS = [
    ("Highly Predictable", 0.1),
    ("Predictable", 0.3),
    ("Balanced", 0.7),
    ("Somewhat Unpredictable", 1.0),
    ("Unpredictable", 1.5),
    ("Highly Unpredictable", 2.0)
]
DEFAULT_PREDICTABILITY = "Balanced"

# Initialize components
config = Config()
core = PromptForgeCore()
prompt_manager = PromptManager()
style_manager = StyleManager()
script_analyzer = ScriptAnalyzer()
meta_chain = MetaChain(core)
core.meta_chain = meta_chain  # Set the meta_chain attribute of the PromptForgeCore instance
prompt_logger = PromptLogger()

@debug_func
async def generate_prompt_wrapper(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters, active_subjects, subjects_json, predictability_index, camera_shot, camera_move):
    try:
        active_subjects_list = [subject.strip() for subject in active_subjects.split(',')] if active_subjects else []
        subjects = json.loads(subjects_json) if subjects_json else []
        
        # Convert predictability index to temperature
        _, temperature = PREDICTABILITY_SETTINGS[int(predictability_index)]
        
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
            temperature=temperature,
            camera_shot=camera_shot,
            camera_move=camera_move
        )
        prompt_logger.log_prompt(result)
        return json.dumps(result, indent=2)
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

def generate_random_style():
    # Placeholder for random style generation
    return "Random Style"

def save_style(style_name, prefix, suffix):
    style_manager.add_style(style_name, prefix, suffix)
    return f"Style '{style_name}' saved successfully."

def generate_style_details(prefix):
    # Placeholder for generating style details based on prefix
    return "Generated style details based on prefix"

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
            
            with gr.Group():
                gr.Markdown("## 🎨 Style")
                style_input = gr.Dropdown(choices=style_manager.get_style_names(), label="Style")
                style_prefix_input = gr.Textbox(label="Style Prefix", placeholder="Enter style name/details")
                style_suffix_input = gr.Textbox(label="Style Suffix", placeholder="Enter style suffix")
                with gr.Row():
                    save_style_button = gr.Button("💾 Save Style")
                    generate_style_details_button = gr.Button("🔍 Generate Style Details")
                generate_random_style_button = gr.Button("🎲 Generate Random Style")
            
            script_input = gr.Textbox(label="📜 Script", lines=10)
            stick_to_script_input = gr.Checkbox(label="📌 Stick to Script")
            highlighted_text_input = gr.Textbox(label="🖍️ Highlighted Text", lines=3)
            
            with gr.Row():
                camera_shot_input = gr.Dropdown(label="🎥 Camera Shot", choices=["Close-up", "Medium shot", "Long shot", "Over-the-shoulder", "Dutch angle"])
                camera_move_input = gr.Dropdown(label="🎬 Camera Move", choices=["Static", "Pan", "Tilt", "Zoom", "Dolly", "Tracking"])
            
            end_parameters_input = gr.Textbox(label="🔧 End Parameters")
            
            predictability_input = gr.Slider(
                minimum=0,
                maximum=len(PREDICTABILITY_SETTINGS) - 1,
                step=1,
                value=next(i for i, (label, _) in enumerate(PREDICTABILITY_SETTINGS) if label == DEFAULT_PREDICTABILITY),
                label="🎲 Predictability",
                info="Adjust the predictability of the generated prompt",
            )

        with gr.Column(scale=1):
            # Right column (Generated Prompt)
            gr.Markdown("## 🖼️ Generated Prompts")
            generated_prompts = gr.JSON(label="Generated Prompts")
            
            with gr.Row():
                save_button = gr.Button("💾 Save Prompts")
                copy_button = gr.Button("📋 Copy Prompts")
                clear_button = gr.Button("🧹 Clear All")
            
            with gr.Group():
                gr.Markdown("## 👤 Subject Details")
                subject_name = gr.Textbox(label="Subject Name")
                subject_category = gr.Dropdown(label="Subject Category", choices=["Person", "Animal", "Place", "Thing", "Other"])
                subject_description = gr.Textbox(label="Subject Description", lines=3)
                add_subject_button = gr.Button("➕ Add Subject")
                subjects_list = gr.JSON(label="Added Subjects")
    
    generate_button = gr.Button("🚀 Generate Prompt")
    feedback_area = gr.Textbox(label="💬 Feedback", interactive=False)
    
    async def generate_prompt_wrapper(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters, active_subjects, camera_shot, camera_move, predictability_index):
        try:
            logger.info("Starting generate_prompt_wrapper")
        
            # Convert predictability index to temperature
            _, temperature = PREDICTABILITY_SETTINGS[int(predictability_index)]
        
            result = await core.meta_chain.generate_prompt(
                style=style,
                highlighted_text=highlighted_text,
                shot_description=shot_description,
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                end_parameters=end_parameters,
                active_subjects=json.loads(active_subjects) if active_subjects else [],
                full_script=script,
                temperature=temperature
            )
            logger.info(f"generate_prompt result: {result}")

            if not isinstance(result, dict):
                logger.error(f"Unexpected result type: {type(result)}")
                return "", "", "", f"Error: Unexpected result type {type(result)}"

            concise = result.get("concise", {}).get("Full Prompt", "")
            normal = result.get("normal", {}).get("Full Prompt", "")
            detailed = result.get("detailed", {}).get("Full Prompt", "")

            logger.info(f"Prompts generated - Concise: {concise[:50]}..., Normal: {normal[:50]}..., Detailed: {detailed[:50]}...")

            return concise, normal, detailed, "Prompt generated successfully"
        except PromptGenerationError as e:
            logger.error(f"Prompt generation error: {str(e)}")
            return "", "", "", f"Error generating prompt: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in generate_prompt_wrapper")
            error_report = get_error_report()
            return "", "", "", f"Unexpected error: {str(e)}\n\nError Report:\n{error_report}"

    generate_button.click(
        generate_prompt_wrapper,
        inputs=[style_input, highlighted_text_input, shot_description_input, 
                directors_notes_input, script_input, stick_to_script_input, 
                end_parameters_input, active_subjects_input, subjects_list, 
                predictability_input, camera_shot_input, camera_move_input],
        outputs=[generated_prompts]
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
    
    def save_prompt_with_name(concise, normal, detailed):
        name = gr.Textbox(label="Enter a name for this prompt set", interactive=True)
        save_button = gr.Button("Save")
        
        def do_save(name):
            if not name:
                return "Please enter a name for the prompt set."
            prompt_manager.save_prompt({
                "concise": concise,
                "normal": normal,
                "detailed": detailed
            }, name)
            return f"Prompt set '{name}' saved successfully."
        
        save_button.click(do_save, inputs=[name], outputs=feedback_area)

    save_button.click(
        save_prompt_with_name, 
        inputs=[concise_output, normal_output, detailed_output]
    )
    
    copy_concise_button.click(lambda x: gr.Textbox.update(value=x), inputs=[concise_output], outputs=[feedback_area])
    copy_normal_button.click(lambda x: gr.Textbox.update(value=x), inputs=[normal_output], outputs=[feedback_area])
    copy_detailed_button.click(lambda x: gr.Textbox.update(value=x), inputs=[detailed_output], outputs=[feedback_area])
    
    def clear_all():
        return ("", "", "", "", "", False, "", "", "", "", "", "", "", "", "", "")
    
    clear_button.click(
        clear_all,
        outputs=[style_input, shot_description_input, directors_notes_input, highlighted_text_input,
                 script_input, stick_to_script_input, camera_shot_input, camera_move_input,
                 end_parameters_input, active_subjects_input,
                 concise_output, normal_output, detailed_output, style_prefix_input, style_suffix_input, subjects_list]
    )

    subjects = []

    def add_subject(name, category, description):
        subjects.append({"name": name, "category": category, "description": description})
        return json.dumps(subjects, indent=2), "", "", ""

    add_subject_button.click(
        add_subject,
        inputs=[subject_name, subject_category, subject_description],
        outputs=[subjects_list, subject_name, subject_category, subject_description]
    )
    
    # Style-related event handlers
    generate_random_style_button.click(generate_random_style, outputs=style_input)
    save_style_button.click(save_style, inputs=[style_input, style_prefix_input, style_suffix_input], outputs=feedback_area)
    generate_style_details_button.click(generate_style_details, inputs=[style_prefix_input], outputs=style_suffix_input)
    
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
