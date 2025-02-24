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

import attr


@attr.s(auto_attribs=True)
class ModuleTransition:
    module_from: str
    module_to: str
    transition_probability: float

    def dump(self, directory: Path):
        fpath = directory / f"{self.module_from}_to_{self.module_to}.json"
        data = {
            "module_from": self.module_from,
            "module_to": self.module_to,
            "transition_probability": self.transition_probability
        }
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath


def process_transitions(df: pd.DataFrame, threshold: float = 0.05, num_modules: int = 5) -> List[ModuleTransition]:
    transition_matrix = df.div(df.sum(axis=1), axis=0).fillna(0)
    transitions = []

    for module_from in transition_matrix.columns:
        for module_to in transition_matrix.columns:
            if module_from != module_to:
                transition_value = transition_matrix.loc[module_from, module_to]

                if transition_value >= threshold:
                    transitions.append(ModuleTransition(
                        module_from=module_from,
                        module_to=module_to,
                        transition_probability=transition_value
                    ))

    return transitions


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    num_modules = options.get("num_modules", 5) if options else 5

    results = extract_roles(config, roles_dir_name, options)

    modules_per_role = defaultdict(list)
    module_transitions = defaultdict(Counter)
    
    for role in results:
        modules_per_role[role.name] = [module.name for module in role.modules]

        module_sequence = modules_per_role[role.name]
        for i in range(len(module_sequence) - 1):
            module_transitions[module_sequence[i]][module_sequence[i + 1]] += 1

    all_modules = sorted(set(module for modules in modules_per_role.values() for module in modules)) 
    module_usage_matrix = {role_id: {module: 0 for module in all_modules} for role_id in sorted(modules_per_role.keys())}  # 🔹 TRI FIXE
    
    for role_id, modules in modules_per_role.items():
        for module in modules:
            module_usage_matrix[role_id][module] += 1

    df_usage = pd.DataFrame.from_dict(module_usage_matrix, orient="index") 

    transition_matrix = pd.DataFrame(0, index=all_modules, columns=all_modules)
    for module_from, transitions in module_transitions.items():
        for module_to, count in transitions.items():
            transition_matrix.loc[module_from, module_to] = count

    transitions = process_transitions(transition_matrix, threshold=0.05, num_modules=num_modules)

    store_results(transitions, config, "Module_Transitions")

    return transitions


def store_results(transitions: List[ModuleTransition], config, filename):
    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    num_modules = config.options.get("num_modules", 5)

    for transition in transitions:
        transition.dump(output_dir)

    print(f"Stockage temporaire terminé : {len(transitions)} fichiers JSON créés dans {output_dir}.")

    transition_data = {(t.module_from, t.module_to): t.transition_probability for t in transitions}

    modules = sorted(set([t.module_from for t in transitions] + [t.module_to for t in transitions]))  

    top_modules = sorted(modules[:num_modules])  

    transition_matrix = pd.DataFrame(index=top_modules, columns=top_modules, data=0.0)

    for (module_from, module_to), value in transition_data.items():
        if module_from in top_modules and module_to in top_modules:
            transition_matrix.at[module_from, module_to] = value
            transition_matrix.at[module_to, module_from] = value

    plt.figure(figsize=(12, 10))
    sns.heatmap(transition_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"Matrice de Transition des {num_modules} Modules les Plus Utilisés")

    transition_image_path = output_dir / "module_transition_matrix.png"
    plt.savefig(transition_image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Matrice de transition enregistrée sous {transition_image_path}")

    for file in output_dir.glob("*.json"):
        file.unlink()

    print(f"Tous les fichiers JSON temporaires ont été supprimés.")
