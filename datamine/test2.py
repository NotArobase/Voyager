import sys
from typing import Any, Dict, Optional
import pandas as pd
import os
from collections import Counter, defaultdict
import csv
import yaml
import seaborn as sns
import matplotlib.pyplot as plt
import util

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    # Call the algo function from test1 to get roles and modules
    return extract_roles(config, roles_dir_name, options)


def store_results(results, config, filename) -> None:
    """Store results in the dataset and generate a correlation heatmap."""
    dataset_dir_path = os.path.join(config.output_directory, filename)
    os.makedirs(dataset_dir_path, exist_ok=True)

    modules_per_role = defaultdict(list)
    module_usage_count = Counter()  # Count total usage for each module

    # Collect module usage data
    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]
        for module in role.modules:
            module_usage_count[module.name] += module.uses

    num_modules = config.options.get("num_modules", 20) if config.options else 20

    # Select top N most used modules
    top_modules = [module for module, _ in module_usage_count.most_common(num_modules)]

    # Initialize the module usage matrix for each role
    module_usage_matrix = {role_id: {module: 0 for module in top_modules} for role_id in modules_per_role}

    # Fill the module usage matrix
    for role_id, modules in modules_per_role.items():
        for module in modules:
            if module in top_modules:
                module_usage_matrix[role_id][module] += 1

    # Export the module usage matrix to a CSV file
    output_file = os.path.join(config.output_directory, filename, "modules_par_role.csv")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Role"] + top_modules)
        for role_id, module_counts in module_usage_matrix.items():
            writer.writerow([role_id] + [module_counts[module] for module in top_modules])

    print(f"Module usage matrix saved to {output_file}.")

    # Read the CSV file into a DataFrame to compute the correlation matrix
    df = pd.read_csv(output_file, index_col=0)
    correlation_matrix = df.corr()

    # Generate and save a heatmap visualization of the correlation matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title(f"Correlation Matrix of Top {num_modules} Most Used Modules")
    plt.savefig(os.path.join(config.output_directory, filename, "correlation_matrix.png"))
    plt.close()

    print(f"Correlation matrix heatmap saved as '{output_file}'.")
