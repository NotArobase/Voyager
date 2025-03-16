import os
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Optional, Dict, Any
import shutil
import sys
from datamine.models import ModuleArguments
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles
import attr

def process_common_args(yaml_files: List[str]) -> List[ModuleArguments]:
    # Dictionary to collect all arguments used per module
    modules_args = defaultdict(list)

    def process_yaml_file(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

            for role in data:
                # Process roles with revision "HEAD" only
                if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                    for task_file in role.get('role_root', {}).get('task_files', []):
                        for task in task_file.get('content', []):
                            for block in task.get('block', []):
                                action = block.get('action')
                                args = block.get('args', {})
                                # Collect argument keys if present
                                if action and isinstance(args, dict):
                                    modules_args[action].extend(args.keys())

    # Process each YAML file provided
    for file_path in yaml_files:
        process_yaml_file(file_path)

    # Identify unique arguments per module
    common_args_per_module = {module: list(set(args)) for module, args in modules_args.items()}

    return [ModuleArguments(module=mod, common_args=args) for mod, args in common_args_per_module.items()]


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    directory_path = os.path.join(config.output_directory, roles_dir_name)

    # Check if the directory exists
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire '{directory_path}' n'existe pas.")

    # Retrieve YAML files from the specified directory
    yaml_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".yaml")]

    # Process YAML files to extract common arguments
    common_args_results = process_common_args(yaml_files)

    return common_args_results


def store_results(common_args_results: List[ModuleArguments], config, filename):
    num_arguments = config.options.get("num_arguments", 25)
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each module's common arguments as JSON files
    for module_args in common_args_results:
        module_args.dump(output_dir)

    print(f"Stockage finisehd : {len(common_args_results)} fichiers JSON créés dans {output_dir}.")

    # Convert results into a dictionary for further processing
    common_args_dict = {mod.module: mod.common_args for mod in common_args_results}

    # Save the overall results to JSON
    json_file_path = output_dir / "common_args_result.json"
    with open(json_file_path, "w") as f:
        json.dump({"data": common_args_dict}, f, indent=2, sort_keys=True)

    # Save the results to CSV format
    csv_file_path = output_dir / "common_args_per_module.csv"
    df = pd.DataFrame.from_dict(common_args_dict, orient='index')
    df.index.name = 'Module'
    df.to_csv(csv_file_path)

    print(f"results are saved in'{json_file_path}' et '{csv_file_path}'.")

    # Count usage frequency of each argument and generate a bar plot
    arg_usage = Counter(arg for args in common_args_dict.values() for arg in args)
    top_args = arg_usage.most_common(num_arguments)

    if top_args:
        args, counts = zip(*top_args)
        plt.figure(figsize=(12, 8))
        sns.barplot(x=list(args), y=list(counts))
        plt.xticks(rotation=90)
        plt.xlabel("Arguments")
        plt.ylabel("Usage Count")
        plt.title(f"Top {num_arguments} Most Used Arguments")
        plt.savefig(output_dir / f"top_{num_arguments}_arguments.png", dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Graphique of {num_arguments} arguments most used")

    # Remove temporary JSON files after completion
    for file in output_dir.glob("*.json"):
        file.unlink()

    print("all json files are deleted")
