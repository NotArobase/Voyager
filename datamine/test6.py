import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from typing import List, Optional, Dict, Any
import sys
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles  

from datamine.models import StrongCorrelation


def process_strong_correlations(df: pd.DataFrame, threshold: float = 0.6) -> List[StrongCorrelation]:
    correlation_matrix = df.corr()
    correlations = []

    for module_a in correlation_matrix.columns:
        for module_b in correlation_matrix.columns:
            if module_a != module_b:
                correlation_value = correlation_matrix.loc[module_a, module_b]

                if abs(correlation_value) >= threshold:
                    correlations.append(StrongCorrelation(
                        module_a=module_a,
                        module_b=module_b,
                        correlation=correlation_value
                    ))

    return correlations


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    directory_path = os.path.join(config.output_directory, roles_dir_name)

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire '{directory_path}' n'existe pas.")

    results = extract_roles(config, roles_dir_name, options)

    modules_per_role = defaultdict(list)
    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]

    all_modules = sorted(set(module for modules in modules_per_role.values() for module in modules))

    module_usage_matrix = {role_id: {module: 0 for module in all_modules} for role_id in sorted(modules_per_role.keys())}
    
    for role_id, modules in modules_per_role.items():
        for module in modules:
            module_usage_matrix[role_id][module] += 1

    df = pd.DataFrame.from_dict(module_usage_matrix, orient="index")

    strong_correlations = process_strong_correlations(df, threshold=0.6)

    #store_results(strong_correlations, config, "StrongModuleCorrelations")

    return strong_correlations


def filter_top_correlations(strong_correlations: List[StrongCorrelation], top_n: int = 20) -> pd.DataFrame:
    """Filtre la matrice de corrélation pour ne garder que les 25 corrélations les plus fortes."""
    if not strong_correlations:
        return pd.DataFrame()

    # Trier par corrélation absolue et prendre les `top_n` plus fortes
    top_correlations = sorted(strong_correlations, key=lambda x: x.correlation, reverse=True)[:top_n]

    # Récupérer les modules impliqués
    modules = sorted(set([corr.module_a for corr in top_correlations] + [corr.module_b for corr in top_correlations]))

    # Construire une nouvelle matrice de corrélation filtrée
    correlation_matrix = pd.DataFrame(index=modules, columns=modules, data=0.0)

    for corr in top_correlations:
        correlation_matrix.at[corr.module_a, corr.module_b] = corr.correlation
        correlation_matrix.at[corr.module_b, corr.module_a] = corr.correlation

    print(f"Modules sélectionnés pour la heatmap : {list(modules)}")

    return correlation_matrix


def store_results(strong_correlations: List[StrongCorrelation], config, filename):
    """Stocke les résultats et génère une heatmap avec seulement les 25 corrélations les plus fortes."""
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    num_modules = config.options.get("num_modules", 25) if config.options else 25

    correlation_data = [
        {"module_a": corr.module_a, "module_b": corr.module_b, "correlation": corr.correlation}
        for corr in strong_correlations
    ]

    json_file_path = output_dir / "strong_correlations.json"
    with open(json_file_path, "w") as f:
        json.dump({"data": correlation_data}, f, indent=2, sort_keys=True)

    csv_file_path = output_dir / "strong_correlations.csv"
    df = pd.DataFrame(correlation_data)
    df.to_csv(csv_file_path, index=False)

    print(f"Les résultats ont été sauvegardés dans '{json_file_path}' et '{csv_file_path}'.")

    # Filtrer pour ne garder que les `num_modules` corrélations les plus fortes
    filtered_matrix = filter_top_correlations(strong_correlations, num_modules)

    if not filtered_matrix.empty:
        plt.figure(figsize=(12, 10))
        sns.heatmap(filtered_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
        plt.title(f"Top {num_modules} Corrélations Fortes entre Modules")

        correlation_image_path = output_dir / "strong_correlation_matrix.png"
        plt.savefig(correlation_image_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Matrice des corrélations fortes enregistrée sous {correlation_image_path}")
    else:
        print("Aucune corrélation forte trouvée, aucune heatmap générée.")

    # Nettoyage des fichiers temporaires JSON
    for file in output_dir.glob("*.json"):
        file.unlink()

    print("Tous les fichiers JSON temporaires ont été supprimés.")
