# PromptForge Comprehensive User Guide

## Table of Contents
1. Introduction
2. System Overview
3. File Structure
4. Detailed Component Breakdown
   4.1 core.py
   4.2 ui.py
   4.3 script_analyzer.py
   4.4 prompt_manager.py
   4.5 meta_chain.py
   4.6 main.py
5. Workflow and Data Flow
6. User Interaction Guide
7. Extending and Customizing PromptForge

## 1. Introduction

PromptForge is an AI-powered application designed to assist creative professionals in generating detailed visual prompts from scripts. It integrates various inputs such as script content, shot descriptions, director's notes, and style preferences to produce comprehensive and contextually rich prompts for visual content creation.

## 2. System Overview

PromptForge consists of several interconnected components:
- Core Logic (core.py)
- User Interface (ui.py)
- Script Analyzer (script_analyzer.py)
- Prompt Manager (prompt_manager.py)
- Meta Chain for prompt generation (meta_chain.py)
- Main execution file (main.py)

These components work together to process user inputs, analyze scripts, and generate tailored prompts.

## 3. File Structure

- main.py: Entry point of the application
- core.py: Central hub of the application logic
- ui.py: Handles the graphical user interface
- script_analyzer.py: Analyzes input scripts for context and entities
- prompt_manager.py: Manages saving and loading of prompts
- meta_chain.py: Orchestrates the prompt generation process

## 4. Detailed Component Breakdown

### 4.1 core.py

This file contains the central logic of PromptForge.

Classes:
1. StyleHandler
   - Manages the style information for prompts
   - Methods:
     - set_prefix(prefix): Sets the style prefix
     - generate_suffix(): Generates a style suffix using AI
     - get_full_style(): Returns the complete style (prefix + suffix)

2. ElementManager
   - Manages the 21 key elements of a visual prompt
   - Methods:
     - update_element(name, value): Updates a specific element
     - get_elements(): Returns all elements

3. PromptForgeCore
   - The main class that orchestrates all components
   - Methods:
     - set_style(style_prefix): Sets the style and generates a suffix
     - process_shot(shot_description): Processes shot description and updates elements
     - process_directors_notes(notes): Processes director's notes and updates elements
     - process_script(highlighted_text, full_script, stick_to_script): Processes script and updates elements
     - generate_prompt(length): Generates a prompt using MetaChain
     - save_prompt(prompt, components): Saves a prompt using PromptManager
     - load_prompt(index): Loads a prompt using PromptManager

### 4.2 ui.py

This file handles the graphical user interface.

Classes:
1. PromptForgeUI
   - Manages the entire user interface
   - Methods:
     - setup_ui(): Sets up all UI components
     - generate_prompt(): Handles the prompt generation process
     - save_prompt(): Handles saving the generated prompt

Functions:
- main(): Entry point for the application, sets up the main window

### 4.3 script_analyzer.py

This file is responsible for analyzing input scripts.

Classes:
1. ScriptAnalyzer
   - Analyzes scripts for entities and context
   - Methods:
     - analyze_script(script): Analyzes the script for entities and context
     - get_entity_description(entity_name): Returns the description of a specific entity
     - get_context_up_to_point(point): Returns the context up to a specific point in the script

### 4.4 prompt_manager.py

This file manages the saving, loading, and organization of prompts.

Classes:
1. PromptManager
   - Handles prompt storage and retrieval
   - Methods:
     - save_prompt(prompt, components): Saves a new prompt
     - load_prompt(index): Loads a specific prompt
     - get_all_prompts(): Returns all saved prompts
     - delete_prompt(index): Deletes a specific prompt
     - search_prompts(keyword): Searches prompts based on a keyword
     - update_prompt(index, prompt, components): Updates an existing prompt

### 4.5 meta_chain.py

This file orchestrates the prompt generation process.

Classes:
1. MetaChain
   - Manages the overall prompt generation process
   - Methods:
     - generate_prompt(length): Generates a prompt based on all gathered information
     - refine_prompt(initial_prompt, feedback): Refines a prompt based on user feedback
     - generate_variations(base_prompt, num_variations): Generates variations of a base prompt

### 4.6 main.py

This is the entry point of the application.

Functions:
- main(): Initializes the application and starts the UI

## 5. Workflow and Data Flow

1. User inputs (style, shot description, director's notes, script) are collected through the UI.
2. The PromptForgeCore processes these inputs:
   - Style is set and a suffix is generated
   - Shot description is processed to update elements
   - Director's notes are processed to further update elements
   - Script is analyzed for context and entities
3. The MetaChain uses all this information to generate a prompt.
4. The generated prompt is displayed in the UI.
5. The user can save the prompt, which is then managed by the PromptManager.

## 6. User Interaction Guide

1. Launch the application by running main.py.
2. Input the desired style in the "Style" field.
3. Describe the shot in the "Shot Description" field.
4. Select a camera move from the dropdown menu.
5. Enter any director's notes in the "Director's Notes" field.
6. Paste your script in the "Script" field and highlight relevant sections.
7. Choose whether to stick to the script using the checkbox.
8. Select the desired prompt length.
9. Click "Generate Prompt" to create a prompt.
10. The generated prompt will appear in the "Generated Prompt" field.
11. You can save the prompt using the "Save Prompt" button.

## 7. Extending and Customizing PromptForge

- To add new elements, modify the ElementManager class in core.py.
- To change the prompt generation logic, modify the MetaChain class in meta_chain.py.
- To add new UI features, modify the PromptForgeUI class in ui.py.
- To enhance script analysis, modify the ScriptAnalyzer class in script_analyzer.py.
- To change how prompts are saved or loaded, modify the PromptManager class in prompt_manager.py.

Remember to maintain the existing method signatures when modifying classes to ensure compatibility with the rest of the system.

# Page 2 Prompt: Comprehensive User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Main Interface](#main-interface)
4. [Input Fields](#input-fields)
5. [Subject Management](#subject-management)
6. [Generating Prompts](#generating-prompts)
7. [Output and Prompt Management](#output-and-prompt-management)
8. [Automated Script Analysis](#automated-script-analysis)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

## 1. Introduction <a name="introduction"></a>

Page 2 Prompt is a powerful tool designed to assist screenwriters, directors, and visual artists in transforming written scripts into detailed visual prompts. This application bridges the gap between the written word and visual conceptualization, making it an invaluable asset for pre-production and storyboarding processes.

## 2. Getting Started <a name="getting-started"></a>

### System Requirements
- Windows 10 or later, macOS 10.14 or later, or a modern Linux distribution
- Python 3.7 or later
- 4GB RAM (8GB recommended)
- 500MB free disk space

### Installation
1. Clone the repository or download the application files.
2. Install required dependencies by running `pip install -r requirements.txt` in your terminal.
3. Launch the application by running `python main.py`.

### First-time Setup
1. Upon first launch, you'll be prompted to enter your OpenAI API key.
2. Click on "Save API Key" to store it securely.

## 3. Main Interface <a name="main-interface"></a>

The Page 2 Prompt interface is divided into several sections:
- Left panel: Input fields for script details and prompt generation settings
- Right panel (top): Generated prompt output area
- Right panel (middle): Subject management
- Right panel (bottom): Automated script analysis

## 4. Input Fields <a name="input-fields"></a>

### Shot Description
Enter a brief description of the shot you want to visualize. Be as specific as possible about the action, setting, and mood.

### Style
Input the visual style you want to achieve. This could be a film genre, a specific director's style, or a particular visual aesthetic.

### Camera Move
Select the camera movement for the shot from the dropdown menu. Options include None, Pan, Tilt, Zoom, Dolly, Truck, and Pedestal.

### Director's Notes
Add any additional notes or specific instructions from the director that should be considered in the prompt generation.

### Script
Paste the relevant portion of your script here. You can highlight specific parts of the script to focus the prompt generation on those elements.

### Stick to Script
Check this box if you want the generated prompt to closely adhere to the script content.

### Prompt Length
Choose between short, medium, or long prompt outputs based on your needs.

## 5. Subject Management <a name="subject-management"></a>

The Subject Management section allows you to create and manage characters, locations, and objects that appear in your script.

### Adding a Subject
1. Enter the subject's name.
2. Select a category (Main Character, Supporting Character, Location, or Object).
3. Provide a brief description.
4. Click "Add Subject".

### Managing Subjects
- Use the "Toggle Active" button to include or exclude a subject from prompt generation.
- Click "Remove Subject" to delete a subject from the list.

## 6. Generating Prompts <a name="generating-prompts"></a>

1. Fill in all relevant input fields.
2. Ensure desired subjects are set as active.
3. Click the "🚀 Generate Prompt" button.
4. The generated prompt will appear in the output area on the right.

## 7. Output and Prompt Management <a name="output-and-prompt-management"></a>

### Saving Prompts
Click the "Save Prompt" button to store the generated prompt for future reference.

### Copying Prompts
Use the "Copy to Clipboard" button to easily copy the prompt for use in other applications.

### Viewing All Prompts
Click "Show All Prompts" to open a new window displaying all previously saved prompts.

### Viewing Logs
The "Show Logs" button opens a window displaying application logs, useful for troubleshooting.

## 8. Automated Script Analysis <a name="automated-script-analysis"></a>

This feature allows you to analyze entire scripts and generate prompts for each scene automatically.

1. Click "Browse" to select your script file.
2. Choose a director's style from the dropdown menu.
3. Click "Analyze Script" to start the process.
4. Results will be displayed in the text area below.

## 9. Advanced Features <a name="advanced-features"></a>

### Refining Prompts
You can refine generated prompts by providing feedback. The application will use this feedback to create an improved version of the prompt.

### Generating Variations
Create multiple variations of a prompt to explore different visual possibilities for the same scene.

## 10. Troubleshooting <a name="troubleshooting"></a>

- If the application freezes, check the logs for any error messages.
- Ensure your API key is correctly entered and saved.
- For script analysis issues, make sure your script file is in a readable format (plain text recommended).
- If prompts are not generating, check your internet connection and API key validity.

For additional support, please refer to our online documentation or contact our support team.

---

This user guide provides a comprehensive overview of Page 2 Prompt's features and functionalities. As you become more familiar with the application, you'll discover how it can significantly enhance your visual storytelling process. Happy prompting!
