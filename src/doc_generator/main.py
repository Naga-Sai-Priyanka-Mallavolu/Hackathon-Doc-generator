#!/usr/bin/env python
import sys
import warnings
import os
from pathlib import Path
from datetime import datetime

from doc_generator.crew import DocGenerator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the documentation generation crew.
    Prompts user for folder path to process the entire codebase.
    """
    print(f"\n{'='*70}")
    print(f"DOCUMENTATION GENERATION SYSTEM")
    print(f"{'='*70}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Prompt user for folder path
    while True:
        folder_path = input("Enter the path to the codebase folder (or press Enter for current directory): ").strip()
        
        # If empty, use current directory
        if not folder_path:
            folder_path = os.getcwd()
            print(f"Using current directory: {folder_path}")
            break
        
        # Validate folder path
        folder = Path(folder_path)
        if not folder.exists():
            print(f"❌ Error: Folder path '{folder_path}' does not exist. Please try again.\n")
            continue
        
        if not folder.is_dir():
            print(f"❌ Error: '{folder_path}' is not a directory. Please try again.\n")
            continue
        
        # Valid path found
        break
    
    # Convert to absolute path
    folder_path = str(Path(folder_path).absolute())
    
    print(f"\n{'='*70}")
    print(f"Processing codebase at: {folder_path}")
    print(f"{'='*70}\n")
    
    inputs = {
        'folder_path': folder_path,
        'timestamp': datetime.now().isoformat(),
    }

    try:
        crew_instance = DocGenerator().crew()
        result = crew_instance.kickoff(inputs=inputs)
        
        # Save result to markdown file
        output_file = Path('technical_documentation.md')
        
        # Priority: Use final_assembly_task output if available, otherwise aggregate
        final_output = None
        all_outputs = []
        
        for task in crew_instance.tasks:
            task_output = task.output
            if task_output:
                output_text = None
                if hasattr(task_output, 'raw'):
                    output_text = task_output.raw
                elif hasattr(task_output, 'result'):
                    output_text = str(task_output.result)
                elif isinstance(task_output, str):
                    output_text = task_output
                elif task_output:
                    output_text = str(task_output)
                
                if output_text and output_text.strip():
                    # Safely get task name
                    task_name = "task"
                    if task.config and isinstance(task.config, dict):
                        task_name = task.config.get('description', 'task')[:50]
                    elif hasattr(task, 'agent') and task.agent:
                        task_name = str(task.agent)[:50]
                    
                    all_outputs.append((task_name, output_text))
                    
                    # Check if this is the final assembly task
                    if task.config and isinstance(task.config, dict) and 'final_assembly' in str(task.config):
                        final_output = output_text
        
        # Use final_assembly output if available, otherwise combine all
        if final_output:
            content = final_output
        elif all_outputs:
            content = f"""# Codebase Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
            content += "\n\n---\n\n".join([out[1] for out in all_outputs])
        else:
            if hasattr(result, 'raw'):
                content = result.raw
            elif isinstance(result, str):
                content = result
            else:
                content = str(result)
        
        # Write to markdown file
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"\n{'='*70}")
        print(f"Documentation generation completed!")
        print(f"Output file: {output_file.absolute()}")
        print(f"Tasks executed: {len(crew_instance.tasks)}")
        print(f"{'='*70}\n")
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    if len(sys.argv) < 3:
        raise Exception("Usage: train <n_iterations> <filename> [folder_path]")
    
    folder_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Error: Invalid folder path '{folder_path}'")
    
    inputs = {
        "folder_path": str(folder.absolute()),
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        DocGenerator().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    if len(sys.argv) < 2:
        raise Exception("Usage: replay <task_id>")
    
    try:
        DocGenerator().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    if len(sys.argv) < 3:
        raise Exception("Usage: test <n_iterations> <eval_llm> [folder_path]")
    
    folder_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Error: Invalid folder path '{folder_path}'")
    
    inputs = {
        "folder_path": str(folder.absolute()),
        "timestamp": datetime.now().isoformat(),
    }

    try:
        DocGenerator().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    folder_path = trigger_payload.get('folder_path', os.getcwd())
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Error: Invalid folder path '{folder_path}'")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "folder_path": str(folder.absolute()),
        "timestamp": datetime.now().isoformat(),
    }

    try:
        result = DocGenerator().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
