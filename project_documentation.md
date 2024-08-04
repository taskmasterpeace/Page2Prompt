# PromptForge Project Documentation

## Core Python Files

### main.py
- Entry point of the application
- Contains the `main()` function that initializes the UI

### ui.py
- Contains the `PageToPromptUI` class
- Manages the user interface using tkinter

### core.py
- Contains the `PromptForgeCore` class
- Manages the core functionality of the application

### meta_chain.py
- Contains the `MetaChain` class
- Manages the prompt generation chain and script analysis

### config.py
- Contains the `Config` class
- Manages application configuration

### prompt_manager.py
- Contains the `PromptManager` class
- Manages saving and loading of prompts

### styles.py
- Contains the `StyleManager` class
- Manages style information for prompts

### script_analyzer.py
- Contains the `ScriptAnalyzer` class
- Analyzes scripts to extract relevant information

### log_analyzer.py
- Contains the `analyze_log()` function
- Analyzes log files to extract usage statistics

### meta_chain_exceptions.py
- Contains custom exception classes for error handling

### prompt_log.py
- Contains the `PromptLogger` class for logging generated prompts

### test_ui.py
- Contains tests for the UI components

## Configuration Files

### config.ini
- Stores configuration settings for the application

### styles.json
- Stores predefined styles for prompt generation

### prompt_templates.json
- Stores templates for prompt generation

## Image Files

### ideal.jpg
- An image file, possibly used as a reference or part of the UI

## Detailed Function Documentation

[Here you would add detailed documentation for each function in your Python files. For example:]

### core.py

#### PromptForgeCore class

##### generate_prompt(self, **kwargs)
- Generates prompts based on user input
- Parameters: [list parameters]
- Returns: [describe return value]

[Continue with similar documentation for all major functions in each file]
