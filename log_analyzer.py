import json
from pprint import pprint
from datetime import datetime, timedelta

def analyze_log(log_file="prompt_log.json", hours=24):
    current_time = datetime.now()
    with open(log_file, "r") as f:
        logs = [json.loads(line) for line in f]
    
    # Sort logs by timestamp, most recent first
    logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    for entry in logs:
        log_time = datetime.fromisoformat(entry['timestamp'])
        if current_time - log_time <= timedelta(hours=hours):
            print(f"Timestamp: {entry['timestamp']}")
            print("Inputs:")
            pprint(entry['inputs'])
            print("\nGenerated Prompt:")
            print(entry['generated_prompt'])
            print("\n" + "="*50 + "\n")
        else:
            break  # Stop when we reach logs older than specified hours

if __name__ == "__main__":
    analyze_log()
