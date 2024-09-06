import gradio as gr
import pandas as pd
from meta_chain import MetaChain
from core import PromptForgeCore

core = PromptForgeCore()  # Initialize PromptForgeCore first
meta_chain = MetaChain(core)  # Then initialize MetaChain
core.meta_chain = meta_chain  # Finally, set the meta_chain attribute of the PromptForgeCore instance

def generate_shot_list(script, director_style):
    # Placeholder for AI-generated shot list
    # This should be replaced with actual logic using meta_chain or core
    shot_list = [
        {"Shot Number": 1, "Description": "Opening scene", "Subjects": "John", "Camera Angle": "Wide shot", "Shot Type": "Establishing", "Completed": False},
        {"Shot Number": 2, "Description": "Close-up of protagonist", "Subjects": "John", "Camera Angle": "Close-up", "Shot Type": "Character intro", "Completed": False},
    ]
    return pd.DataFrame(shot_list)

def update_shot_list(shot_list, row, col, value):
    shot_list.iloc[row, col] = value
    return shot_list

def export_csv(shot_list):
    return shot_list.to_csv(index=False)

with gr.Blocks() as app:
    with gr.Tab("Shot List"):
        script_input = gr.Textbox(label="Script Input", lines=10)
        director_style = gr.Dropdown(label="Director's Style", choices=core.get_director_styles())
        
        generate_button = gr.Button("Generate Shot List")
        
        shot_list_display = gr.DataFrame(label="Shot List", interactive=True)
        
        export_button = gr.Button("Export to CSV")
        csv_output = gr.File(label="Download CSV")
        
        generate_button.click(
            generate_shot_list,
            inputs=[script_input, director_style],
            outputs=[shot_list_display]
        )
        
        shot_list_display.edit(
            update_shot_list,
            inputs=[shot_list_display],
            outputs=[shot_list_display]
        )
        
        export_button.click(
            export_csv,
            inputs=[shot_list_display],
            outputs=[csv_output]
        )

    # Existing tabs and components...
    with gr.Tab("Prompt Generation"):
        api_key = gr.Textbox(label="API Key")
        shot_description = gr.Textbox(label="Shot Description")
        directors_notes = gr.Textbox(label="Director's Notes")
        style = gr.Dropdown(label="Style", choices=["Style1", "Style2", "Style3"])
        prefix = gr.Textbox(label="Prefix")
        suffix = gr.Textbox(label="Suffix")
        script = gr.Textbox(label="Script")
        stick_to_script = gr.Checkbox(label="Stick to Script")
        camera_shot = gr.Dropdown(label="Camera Shot", choices=["Shot1", "Shot2", "Shot3"])
        camera_move = gr.Dropdown(label="Camera Move", choices=["Move1", "Move2", "Move3"])
        end_parameters = gr.Textbox(label="End Parameters")

        generated_prompt = gr.Textbox(label="Generated Prompt")
        save_prompt = gr.Button("Save Prompt")
        copy_to_clipboard = gr.Button("Copy to Clipboard")
        clear_prompts = gr.Button("Clear Prompts")
        show_all_prompts = gr.Button("Show All Prompts")
        show_logs = gr.Button("Show Logs")

        # Define event handlers
        def on_save_prompt():
            core.save_prompt(generated_prompt.get_value())

        def on_copy_to_clipboard():
            gr.Clipboard.copy(generated_prompt.get_value())

        def on_clear_prompts():
            core.clear_prompts()

        def on_show_all_prompts():
            all_prompts = core.get_all_prompts()
            print(all_prompts)

        def on_show_logs():
            print("Show Logs button clicked")

        # Connect event handlers to buttons
        save_prompt.click(on_save_prompt)
        copy_to_clipboard.click(on_copy_to_clipboard)
        clear_prompts.click(on_clear_prompts)
        show_all_prompts.click(on_show_all_prompts)
        show_logs.click(on_show_logs)

app.launch()
