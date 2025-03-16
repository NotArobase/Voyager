from collections import Counter, defaultdict
import csv
import os
import yaml
from models.datamine.roles import Module, MostUsedRoles
from typing import Optional, Dict, Any
import util

def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    """Go over each role and read the YAML files obtained from the previous stage."""
    num_modules = options.get("num_modules", 8) if options else 8

    roles_directory_path = os.path.join(config.output_directory, roles_dir_name)
    modules_per_role = defaultdict(lambda: Counter())  # Counts module usage per role
    role_ids = []  # List to store role IDs

    # Check if roles directory exists
    if not os.path.exists(roles_directory_path):
        raise FileNotFoundError(f"Roles directory '{roles_directory_path}' does not exist.")

    # Internal function to process each YAML file
    def process_yaml_file(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)  # Load YAML data
            inc = 1  # Counter to check the last iteration

            for role in data:
                if isinstance(role, dict):
                    role_id = role.get('role_id')
                    print(f"Processing role with ID: {role_id}")
                    inc += 1
                    role_rev = role.get('role_rev')
                    task_files = role.get('role_root', {}).get('task_files', [])

                    # Check if revision is "HEAD" or last iteration
                    if role_rev == "HEAD" or inc == len(data):
                        role_ids.append(role_id)  # Add role_id to the list

                        # Iterate through task files associated with the role
                        for task_file in task_files:
                            tasks = task_file.get('content', [])
                            for task in tasks:
                                for block in task.get('block', []):
                                    action = block.get('action')
                                    if action:
                                        modules_per_role[role_id][action] += 1  # Count each action (module)
                else:
                    print(f"File '{file_path}' to be checked: {role}")
                    print(f"Problematic filename: {file_path}")

    # Process all YAML files in the directory
    for filename in os.listdir(roles_directory_path):
        if filename.endswith(".yaml"):
            process_yaml_file(os.path.join(roles_directory_path, filename))

    # Check for duplicated roles
    role_counts = Counter(role_ids)
    duplicated_roles = {role_id: count for role_id, count in role_counts.items() if count > 1}

    if duplicated_roles:
        print("Duplicated roles detected:", duplicated_roles)

    # Create the final list of most used roles with associated modules
    most_used_roles = []
    for role_id, actions in modules_per_role.items():
        modules = [Module(name=action, uses=count) for action, count in actions.items()]
        most_used_roles.append(MostUsedRoles(name=role_id, modules=modules))

    print(most_used_roles)
    return most_used_roles


def store_results(results, config, filename) -> None:
    num_modules = config.options.get("num_modules", 20) if config.options else 20
    """Store the results of a stage in the dataset."""
    dataset_dir_path = os.path.join(config.output_directory, filename)
    os.makedirs(dataset_dir_path, exist_ok=True)

    modules_per_role = defaultdict(list)
    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]

    num_modules = config.options.get("num_modules", 20) if config.options else 20

    # Create a set of unique modules, limited to num_modules
    all_modules = list(set(module for modules in modules_per_role.values() for module in modules))[:num_modules]

    # Initialize module usage matrix
    module_usage_matrix = {role_id: {module: 0 for module in all_modules} for role_id in modules_per_role}

    # Populate the matrix with module occurrences
    for role_id, modules in modules_per_role.items():
        for module in modules:
            if module in all_modules:
                module_usage_matrix[role_id][module] += 1

    # Calculate overall module usage
    module_usage = {module: 0 for module in all_modules}
    for role_id, module_counts in module_usage_matrix.items():
        for module, count in module_counts.items():
            module_usage[module] += count

    sorted_usage = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)
    top_50_modules = sorted_usage[:num_modules]

    # Prepare data for plotting
    modules, counts = zip(*top_50_modules)

    # Generate bar chart for the most used modules
    util.create_bar_chart(
        x_data=modules,
        y_data=counts,
        title=f"Top {num_modules} Most Used Modules",
        xlabel="Modules",
        ylabel="Usage Count",
        output_directory=config.output_directory,
        output_dataset_name=filename,
        output_filename=f"top_{num_modules}_modules.png",
        figsize=(12, 8),
    )

    # The following code to delete the CSV file is commented out
    """
    csv_file_path = os.path.join(config.output_directory, filename, "modules_par_role.csv")
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    """
