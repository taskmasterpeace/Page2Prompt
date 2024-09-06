import argparse
import asyncio
import csv
from gradio_meta_chain import MetaChain
from gradio_core import PromptForgeCore

async def generate_shot_list(script_path, director_style, output_path):
    core = PromptForgeCore()
    meta_chain = MetaChain(core)
    
    with open(script_path, 'r') as script_file:
        script_content = script_file.read()
    
    shot_list = await meta_chain.analyze_script(script_content, director_style)
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['Scene Number', 'Shot Number', 'Script Content', 'Shot Description', 'Characters', 'Camera Work', 'Shot Type', 'Completed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for shot in shot_list:
            writer.writerow(shot)

def main():
    parser = argparse.ArgumentParser(description='Generate a shot list from a script.')
    parser.add_argument('--script', required=True, help='Path to the script file')
    parser.add_argument('--director_style', required=True, help='Director style to use')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    asyncio.run(generate_shot_list(args.script, args.director_style, args.output))
    print(f"Shot list generated and saved to {args.output}")

if __name__ == "__main__":
    main()
