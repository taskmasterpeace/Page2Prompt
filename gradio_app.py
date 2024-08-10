import gradio as gr
import asyncio
from gradio_core import PromptForgeCore
from gradio_config import Config, get_openai_api_key
from gradio_prompt_manager import PromptManager
from gradio_styles import StyleManager
from gradio_script_analyzer import ScriptAnalyzer
from gradio_meta_chain import MetaChain
from gradio_prompt_log import PromptLogger
from gradio_meta_chain_exceptions import MetaChainException, PromptGenerationError, ScriptAnalysisError

# Initialize components
config = Config()
core = PromptForgeCore()
prompt_manager = PromptManager()
style_manager = StyleManager()
script_analyzer = ScriptAnalyzer()
meta_chain = MetaChain(core)
prompt_logger = PromptLogger()

# Set up OpenAI API key
openai_api_key = get_openai_api_key()
if openai_api_key:
    import openai
    openai.api_key = openai_api_key
else:
    print("Warning: OpenAI API key not found. Some features may not work.")

async def generate_prompt(style, highlighted_text, shot_description, directors_notes, script, stick_to_script, end_parameters):
    try:
        result = await core.generate_prompt(
            style=style,
            highlighted_text=highlighted_text,
            shot_description=shot_description,
            directors_notes=directors_notes,
            script=script,
            stick_to_script=stick_to_script,
            end_parameters=end_parameters
        )
        prompt_logger.log_prompt(result)
        return result["Concise Prompt"], result["Normal Prompt"], result["Detailed Prompt"]
    except PromptGenerationError as e:
        return f"Error generating prompt: {str(e)}", "", ""
    except Exception as e:
        return f"Unexpected error: {str(e)}", "", ""

async def analyze_script(script_content, director_style):
    try:
        return await core.analyze_script(script_content, director_style)
    except ScriptAnalysisError as e:
        return f"Error analyzing script: {str(e)}"
    except Exception as e:
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

def load_prompt(name):
    try:
        prompts = prompt_manager.get_all_prompts()
        for prompt in prompts:
            if prompt.get("name") == name:
                return prompt.get("formatted_prompt", "Prompt not found")
        return "Prompt not found"
    except Exception as e:
        return f"Error loading prompt: {str(e)}"

def get_prompt_logs():
    return prompt_logger.get_logs()

# Define Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# PromptForge")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Left column
            style_input = gr.Dropdown(choices=style_manager.get_style_names(), label="Style")
            shot_description_input = gr.Textbox(label="Shot Description")
            directors_notes_input = gr.Textbox(label="Director's Notes")
            highlighted_text_input = gr.Textbox(label="Highlighted Text", lines=3)
            script_input = gr.Textbox(label="Script", lines=5)
            stick_to_script_input = gr.Checkbox(label="Stick to Script")
            end_parameters_input = gr.Textbox(label="End Parameters")
        
        with gr.Column(scale=1):
            # Right column
            concise_output = gr.Textbox(label="Concise Prompt")
            normal_output = gr.Textbox(label="Normal Prompt")
            detailed_output = gr.Textbox(label="Detailed Prompt")
            
            with gr.Row():
                save_button = gr.Button("Save Prompt")
                copy_button = gr.Button("Copy to Clipboard")
                clear_button = gr.Button("Clear Prompts")
    
    generate_button = gr.Button("Generate Prompt")
    
    generate_button.click(
        lambda *args: asyncio.run(generate_prompt(*args)),
        inputs=[style_input, shot_description_input, 
                directors_notes_input, script_input, stick_to_script_input, end_parameters_input],
        outputs=[concise_output, normal_output, detailed_output]
    )
    
    # Add event handlers for save, copy, and clear buttons
    save_button.click(save_prompt, inputs=[normal_output, "Untitled"], outputs=gr.Textbox(label="Save Result"))
    copy_concise_button = gr.Button("Copy Concise")
    copy_normal_button = gr.Button("Copy Normal")
    copy_detailed_button = gr.Button("Copy Detailed")
    
    copy_concise_button.click(lambda x: gr.Textbox.update(value=x), inputs=[concise_output], outputs=[gr.Textbox()])
    copy_normal_button.click(lambda x: gr.Textbox.update(value=x), inputs=[normal_output], outputs=[gr.Textbox()])
    copy_detailed_button.click(lambda x: gr.Textbox.update(value=x), inputs=[detailed_output], outputs=[gr.Textbox()])
    def clear_all():
        return ("", "", "", "", "", "", "", "", "", "")
    
    clear_button.click(
        clear_all,
        outputs=[style_input, shot_description_input, directors_notes_input, highlighted_text_input,
                 script_input, stick_to_script_input, end_parameters_input,
                 concise_output, normal_output, detailed_output]
    )
    
    # Script Analysis (can be added as a separate tab or integrated into the main interface)
    with gr.Tab("Script Analysis"):
        script_analysis_input = gr.Textbox(label="Script to Analyze", lines=10)
        director_style_input = gr.Dropdown(choices=core.get_director_styles(), label="Director Style")
        analyze_button = gr.Button("Analyze Script")
        analysis_output = gr.Textbox(label="Analysis Result")
        
        analyze_button.click(
            lambda *args: asyncio.run(analyze_script(*args)),
            inputs=[script_analysis_input, director_style_input], 
            outputs=analysis_output
        )
    
    # Prompt Logs (can be added as a separate tab or integrated into the main interface)
    with gr.Tab("Prompt Logs"):
        log_output = gr.JSON(label="Prompt Generation Logs")
        refresh_logs_button = gr.Button("Refresh Logs")
        
        refresh_logs_button.click(get_prompt_logs, inputs=None, outputs=log_output)

if __name__ == "__main__":
    app.launch(share=True)
