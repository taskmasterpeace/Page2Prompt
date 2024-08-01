import json
from pprint import pprint

def analyze_log(log_file="prompt_log.json"):
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line)
            print(f"Timestamp: {entry['timestamp']}")
            print("Inputs:")
            pprint(entry['inputs'])
            print("\nGenerated Prompt:")
            print(entry['generated_prompt'])
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    analyze_log()
