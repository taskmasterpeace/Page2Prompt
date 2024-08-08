import gradio as gr
from meta_chain import MetaChain
from core import PromptForgeCore

core = PromptForgeCore()  # Initialize PromptForgeCore first
meta_chain = MetaChain(core)  # Then initialize MetaChain
core.meta_chain = meta_chain  # Finally, set the meta_chain attribute of the PromptForgeCore instance

def helper_function(text):
    # Use MetaChain or PromptForgeCore to process the text
    processed_text = meta_chain.process_text(text)  # Replace with actual method
    return processed_text

with gr.Blocks() as app:
    # Define components
    api_key = gr.Textbox(label="API Key")
    shot_description = gr.Textbox(label="Shot Description")
    directors_notes = gr.Textbox(label="Director's Notes")
    style = gr.Dropdown(label="Style", choices=["Style1", "Style2", "Style3"])  # Added style choices
    prefix = gr.Textbox(label="Prefix")
    suffix = gr.Textbox(label="Suffix")
    script = gr.Textbox(label="Script")
    stick_to_script = gr.Checkbox(label="Stick to Script")
    camera_shot = gr.Dropdown(label="Camera Shot", choices=["Shot1", "Shot2", "Shot3"])  # Added camera shot choices
    camera_move = gr.Dropdown(label="Camera Move", choices=["Move1", "Move2", "Move3"])  # Added camera move choices
    end_parameters = gr.Textbox(label="End Parameters")

    generated_prompt = gr.Textbox(label="Generated Prompt")
    save_prompt = gr.Button("Save Prompt")
    copy_to_clipboard = gr.Button("Copy to Clipboard")
    clear_prompts = gr.Button("Clear Prompts")
    show_all_prompts = gr.Button(label="Show All Prompts")
    show_logs = gr.Button(label="Show Logs")

    # Define event handlers
    def on_save_prompt():
        # Use PromptForgeCore to save the prompt
        core.save_prompt(generated_prompt.get_value())  # Replace with actual method

    def on_copy_to_clipboard():
        # Use Gradio's Clipboard API to copy the prompt to the clipboard
        gr.Clipboard.copy(generated_prompt.get_value())

    def on_clear_prompts():
        # Use PromptForgeCore to clear the prompts
        core.clear_prompts()  # Replace with actual method

    def on_show_all_prompts():
        # Use PromptForgeCore to get all prompts and display them
        all_prompts = core.get_all_prompts()  # Replace with actual method
        print(all_prompts)

    def on_show_logs():
        # Use your application's logging system to show logs
        print("Show Logs button clicked")  # Replace with actual implementation

    # Connect event handlers to buttons
    save_prompt.on_click(on_save_prompt)
    copy_to_clipboard.on_click(on_copy_to_clipboard)
    clear_prompts.on_click(on_clear_prompts)
    show_all_prompts.on_click(on_show_all_prompts)
    show_logs.on_click(on_show_logs)

app.launch()
