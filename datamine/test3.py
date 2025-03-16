import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Optional, Dict, Any
import shutil
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles


def process_transitions(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """Normalize the transition matrix and return a filtered version based on threshold."""
    transition_matrix = df.div(df.sum(axis=1), axis=0).fillna(0)

    print("\nTransition matrix after normalization:\n", transition_matrix)

    return transition_matrix


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    num_modules = options.get("num_modules", 20) if options else 20

    results = extract_roles(config, roles_dir_name, options)

    modules_per_role = defaultdict(list)
    module_transitions = defaultdict(Counter)

    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]
        print(f"Role: {role.name} -> Modules: {modules_per_role[role.name]}")

        module_sequence = modules_per_role[role.name]
        print(f"Module sequence for {role.name}: {module_sequence}")

        for i in range(len(module_sequence) - 1):
            module_transitions[module_sequence[i]][module_sequence[i + 1]] += 1

    all_modules = sorted(set(module for modules in modules_per_role.values() for module in modules))
    print("Complete list of extracted modules:", all_modules)

    transition_matrix = pd.DataFrame(0, index=all_modules, columns=all_modules)
    for module_from, transitions in module_transitions.items():
        for module_to, count in transitions.items():
            transition_matrix.loc[module_from, module_to] = count
            print(f"Transition counted: {module_from} → {module_to} = {count}")

    print("\nTransition matrix before normalization:\n", transition_matrix)

    transition_matrix_normalized = process_transitions(transition_matrix)

    return transition_matrix_normalized


def filter_top_modules(transition_matrix: pd.DataFrame, num_modules: int = 20) -> pd.DataFrame:
    """Filter the transition matrix to retain only the top N most-used modules."""
    module_usage = transition_matrix.sum(axis=1) + transition_matrix.sum(axis=0)
    print("Module usage:", module_usage)
    top_modules = module_usage.nlargest(num_modules).index

    print(f"Modules selected for the heatmap: {list(top_modules)}")

    return transition_matrix.loc[top_modules, top_modules]


def store_results(transition_matrix: pd.DataFrame, config, filename):
    """Store results and generate a heatmap for only the most-used modules."""
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    num_modules = 300000  # Large number to display all modules in the CSV

    filtered_matrix = filter_top_modules(transition_matrix, num_modules)

    # Save the filtered transition matrix to a detailed CSV format
    csv_output_path = output_dir / "module_transition_matrix.csv"
    filtered_matrix.reset_index().melt(id_vars='index', var_name='to', value_name='transition_rate') \
        .rename(columns={'index': 'from'}) \
        .to_csv(csv_output_path, index=False, float_format="%.3f")

    print(f"\nTransition matrix saved at {csv_output_path}")

    num_modules = config.options.get("num_modules", 20) if config.options else 20

    filtered_matrix = filter_top_modules(transition_matrix, num_modules)

    print("\nTransition matrix used for heatmap (most-used modules):\n", filtered_matrix)

    plt.figure(figsize=(10, 8))
    sns.heatmap(filtered_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"Top {num_modules} Most Used Modules - Transition Matrix")

    transition_image_path = output_dir / "module_transition_matrix.png"
    plt.savefig(transition_image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\nHeatmap saved at {transition_image_path}")
