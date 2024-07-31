import json
from datetime import datetime

class PromptLogger:
    def __init__(self, log_file="prompt_log.json"):
        self.log_file = log_file

    def log_prompt(self, inputs, generated_prompt):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "inputs": inputs,
            "generated_prompt": generated_prompt
        }
        
        try:
            with open(self.log_file, "r+") as file:
                try:
                    logs = json.load(file)
                except json.JSONDecodeError:
                    logs = []
                logs.append(log_entry)
                file.seek(0)
                json.dump(logs, file, indent=2)
                file.truncate()
        except FileNotFoundError:
            with open(self.log_file, "w") as file:
                json.dump([log_entry], file, indent=2)

    def get_logs(self):
        try:
            with open(self.log_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
import json
from datetime import datetime

class PromptLogger:
    def __init__(self, log_file="prompt_log.json"):
        self.log_file = log_file

    def log_prompt(self, inputs, generated_prompt):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "inputs": inputs,
            "generated_prompt": generated_prompt
        }
        
        try:
            with open(self.log_file, "a") as f:
                json.dump(log_entry, f)
                f.write("\n")  # Add a newline for readability between entries
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_logs(self):
        logs = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    logs.append(json.loads(line))
        except FileNotFoundError:
            print("Log file not found. No logs available.")
        except json.JSONDecodeError:
            print("Error decoding log file. Some logs may be corrupted.")
        return logs
