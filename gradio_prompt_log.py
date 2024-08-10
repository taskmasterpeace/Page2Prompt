import json
from datetime import datetime

class PromptLogger:
    def __init__(self, log_file="prompt_log.json"):
        self.log_file = log_file

    def log_prompt(self, prompt_data):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_data": prompt_data
        }
        with open(self.log_file, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

    def get_logs(self):
        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                logs.append(json.loads(line))
        return logs
