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
from models.datamine.roles import Model, ModuleTransition

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test1 import algo as extract_roles


def process_transitions(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """Normalise la matrice de transition et renvoie une version filtrée selon le seuil."""
    transition_matrix = df.div(df.sum(axis=1), axis=0).fillna(0)

    print("\n📌 Matrice de transition après normalisation :\n", transition_matrix)

    return transition_matrix


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    num_modules = options.get("num_modules", 5) if options else 5

    results = extract_roles(config, roles_dir_name, options)

    modules_per_role = defaultdict(list)
    module_transitions = defaultdict(Counter)

    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]
        print(f"📌 Rôle: {role.name} -> Modules: {modules_per_role[role.name]}")

        module_sequence = modules_per_role[role.name]
        print(f"📌 Séquence des modules pour {role.name}: {module_sequence}")

        for i in range(len(module_sequence) - 1):
            module_transitions[module_sequence[i]][module_sequence[i + 1]] += 1

    all_modules = sorted(set(module for modules in modules_per_role.values() for module in modules))
    print("📌 Liste complète des modules extraits:", all_modules)

    transition_matrix = pd.DataFrame(0, index=all_modules, columns=all_modules)
    for module_from, transitions in module_transitions.items():
        for module_to, count in transitions.items():
            transition_matrix.loc[module_from, module_to] = count
            print(f"📌 Transition comptée: {module_from} → {module_to} = {count}")

    print("\n📌 Matrice de transition avant normalisation :\n", transition_matrix)

    # 🔥 **Correction : Utiliser exactement cette matrice normalisée partout**
    transition_matrix_normalized = process_transitions(transition_matrix)

    # 🔥 **On passe la matrice normalisée sans modifications**
    store_results(transition_matrix_normalized, config, "Module_Transitions")

    return transition_matrix_normalized


def store_results(transition_matrix: pd.DataFrame, config, filename):
    """Stocke les résultats et génère la heatmap."""
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n📌 Matrice de transition utilisée pour la heatmap :\n", transition_matrix)

    print(f"📌 Min : {transition_matrix.min().min()}, Max : {transition_matrix.max().max()}")

    plt.figure(figsize=(12, 10))
    sns.heatmap(transition_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"Matrice de Transition des Modules les Plus Utilisés")

    transition_image_path = output_dir / "module_transition_matrix.png"
    plt.savefig(transition_image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\n📌 Matrice de transition enregistrée sous {transition_image_path}")
