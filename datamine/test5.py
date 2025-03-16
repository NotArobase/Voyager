import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Optional
import sys
import yaml
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles
from pathlib import Path
import json
import sys
sys.path.append(os.path.dirname(os.path.abspath('.')))
from datamine.models import LoopUsage


def process_loop_usage(yaml_files: List[str]) -> List[LoopUsage]:
    """Process YAML files to calculate loop usage percentage for each module."""
    loop_usage = defaultdict(lambda: [0, 0])  # Dictionary to store total actions and actions using loops

    def process_yaml_file(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)  # Load YAML content

            for role in data:
                if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                    for task_file in role.get('role_root', {}).get('task_files', []):
                        for task in task_file.get('content', []):
                            for block in task.get('block', []):
                                action = block.get('action')
                                if action:
                                    loop_usage[action][0] += 1  # Increment total action count
                                    if 'loop' in block:
                                        loop_usage[action][1] += 1  # Increment loop count for the action

    # Process each YAML file
    for yaml_file in yaml_files:
        process_yaml_file(yaml_file)

    # Calculate loop usage percentage per module
    loop_usage_results = []
    for module, (total, looped) in loop_usage.items():
        percentage = (loop_usage[module][1] / loop_usage[module][0]) * 100 if loop_usage[module][0] > 0 else 0
        loop_usage_results.append(LoopUsage(module=module, loop_percentage=percentage))

    return loop_usage_results


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    directory_path = os.path.join(config.output_directory, roles_dir_name)

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist.")

    yaml_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".yaml")]

    loop_usage_results = process_loop_usage(yaml_files)

    store_results(loop_usage_results, config, "LoopUsageAnalysis")

    return loop_usage_results


def store_results(loop_usage_results: List[LoopUsage], config, filename):
    """Store results, save detailed CSV and generate bar chart for loop usage."""
    num_modules = config.options.get("num_modules", 20)

    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each module's loop usage as a JSON file
    for loop_usage in loop_usage_results:
        loop_usage.dump(output_dir)

    print(f"Temporary storage completed: {len(loop_usage_results)} JSON files created in {output_dir}.")

    # Save overall loop usage results to JSON and CSV
    loop_usage_dict = {usage.module: usage.loop_percentage for usage in loop_usage_results}

    json_file_path = output_dir / "loop_usage_result.json"
    with open(json_file_path, "w") as f:
        json.dump({"data": loop_usage_dict}, f, indent=2)

    csv_file_path = output_dir / "loop_usage_percentage.csv"
    pd.DataFrame.from_dict(loop_usage_dict, orient='index', columns=['Loop Usage Percentage']) \
        .to_csv(csv_file_path, index_label="Module")

    print(f"Results stored at '{json_file_path}' and '{csv_file_path}'.")

    # Generate and save a bar chart for the top N modules based on loop usage
    top_loop_usage = sorted(loop_usage_dict.items(), key=lambda x: x[1], reverse=True)[:num_modules]

    if top_loop_usage:
        modules, percentages = zip(*top_loop_usage)
        plt.figure(figsize=(12, 8))
        sns.barplot(x=list(modules), y=list(percentages))
        plt.title(f"Top {num_modules} Modules Using Loops")
        plt.xlabel("Modules")
        plt.ylabel("Loop Usage Percentage")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_dir / f"top_{num_modules}_loop_usage.png", dpi=300)
        plt.close()

        print(f"Bar chart created at {output_dir}/top_{num_modules}_loop_usage.png")

    # Delete temporary JSON files
    for file in output_dir.glob("*.json"):
        file.unlink()

    print("All temporary JSON files have been deleted.")
