import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from typing import List, Optional, Dict, Any
from models.datamine.roles import Model, ModuleCorrelation
import sys
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles

import attr


def process_correlations(df: pd.DataFrame, threshold: float = 0.5, num_modules: int = 5) -> List[ModuleCorrelation]:
    correlation_matrix = df.corr()
    correlations = []

    for module_a in correlation_matrix.columns:
        for module_b in correlation_matrix.columns:
            if module_a != module_b:
                correlation_value = correlation_matrix.loc[module_a, module_b]
                
                if abs(correlation_value) >= threshold:
                    correlations.append(ModuleCorrelation(
                        module_a=module_a,
                        module_b=module_b,
                        correlation=correlation_value
                    ))

    return correlations


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    num_modules = options.get("num_modules", 5) if options else 5

    results = extract_roles(config, roles_dir_name, options)

    modules_per_role = defaultdict(list)
    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]

    all_modules = sorted(set(module for modules in modules_per_role.values() for module in modules))  

    module_usage_matrix = {role_id: {module: 0 for module in all_modules} for role_id in sorted(modules_per_role.keys())}  # 🔹 TRI DES RÔLES
    
    for role_id, modules in modules_per_role.items():
        for module in modules:
            module_usage_matrix[role_id][module] += 1

    df = pd.DataFrame.from_dict(module_usage_matrix, orient="index")  

    correlations = process_correlations(df, threshold=0.6, num_modules=num_modules)

    store_results(correlations, config, "Datamine")

    return correlations


def store_results(correlations: List[ModuleCorrelation], config, filename):
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    num_modules = config.options.get("num_modules", 5)

    for correlation in correlations:
        correlation.dump(output_dir)

    print(f"Stockage temporaire terminé : {len(correlations)} fichiers JSON créés dans {output_dir}.")

    correlation_data = {(corr.module_a, corr.module_b): corr.correlation for corr in correlations}

    modules = sorted(set([corr.module_a for corr in correlations] + [corr.module_b for corr in correlations]))  # 🔹 TRI FIXE

    top_modules = sorted(modules[:num_modules])  

    correlation_matrix = pd.DataFrame(index=top_modules, columns=top_modules, data=0.0)

    for (module_a, module_b), value in correlation_data.items():
        if module_a in top_modules and module_b in top_modules:
            correlation_matrix.at[module_a, module_b] = value
            correlation_matrix.at[module_b, module_a] = value  

    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt=".1f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"Matrice de Corrélation des {num_modules} Modules les Plus Utilisés")

    correlation_image_path = output_dir / "correlation_matrix.png"
    plt.savefig(correlation_image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Matrice de corrélation enregistrée sous {correlation_image_path}")

    for file in output_dir.glob("*.json"):
        file.unlink()

