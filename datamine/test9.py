import os
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from pathlib import Path
from typing import List, Dict, Optional, Any
import re
import attr
from datamine.models import ModuleConditions
def process_module_conditions(yaml_files: List[str]) -> List[ModuleConditions]:
    module_conditions = defaultdict(list)

    def process_yaml_file(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

            if not data:
                print(f" Le fichier {file_path} est vide ou mal formé, ignoré.")
                return

            for role in data:
                if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                    for task_file in role.get('role_root', {}).get('task_files', []):
                        for task in task_file.get('content', []):
                            for block in task.get('block', []):
                                module = block.get('action')
                                condition = block.get('when')

                                if module and condition:
                                    if isinstance(condition, list):
                                        module_conditions[module].extend(condition)
                                    else:
                                        module_conditions[module].append(condition)

    for file in yaml_files:
        process_yaml_file(file)

    return [ModuleConditions(module=mod, conditions=list(set(conds))) for mod, conds in module_conditions.items()]


def algo(config, roles_dir_name: str, options: Optional[Dict[str, Any]] = None):
    directory_path = os.path.join(config.output_directory, roles_dir_name)

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire '{directory_path}' n'existe pas.")

    yaml_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".yaml")]

    module_conditions = process_module_conditions(yaml_files)

    if not module_conditions:
        print("Aucun module avec condition `when` trouvé.")
        return

    #store_results(module_conditions, config, "Datamine")

    return module_conditions

def split_conditions(condition: str) -> Dict[str, List[str]]:
    condition = condition.lower().strip()
    final_conditions = {'and': [], 'or': []}

    match_and_or = re.match(r"^(.*?)\s+and\s+\((.*?)\)$", condition)
    if match_and_or:
        first_part = match_and_or.group(1).strip()  # A
        or_part = match_and_or.group(2).strip()  # B or C

        or_conditions = [c.strip() for c in re.split(r'\s+or\s+', or_part)]
        
        final_conditions['and'].append(first_part)
        final_conditions['and'].append(f"({or_part})")  

        # Ajout à OR
        final_conditions['or'].extend(or_conditions)

        return final_conditions

    match_or_and = re.match(r"^(.*?)\s+or\s+\((.*?)\)$", condition)
    if match_or_and:
        first_part = match_or_and.group(1).strip()  # A
        and_part = match_or_and.group(2).strip()  # B and C

        and_conditions = [c.strip() for c in re.split(r'\s+and\s+', and_part)]
        
        final_conditions['or'].append(first_part)
        final_conditions['or'].append(f"({and_part})")  

        final_conditions['and'].extend(and_conditions)

        return final_conditions

    # Cas normal sans parenthèses : séparation standard
    and_conditions = [c.strip() for c in re.split(r'\s+and\s+', condition)]
    for cond in and_conditions:
        if ' or ' in cond:
            or_subconds = [c.strip() for c in re.split(r'\s+or\s+', cond)]
            final_conditions['or'].extend(or_subconds)
        else:
            final_conditions['and'].append(cond)

    return final_conditions

def store_results(module_conditions: List[Any], config, filename):

    limit_number = config.options.get("num_modules", 25) if config.options else 25

    output_dir = Path(config.output_directory) / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    for module_cond in module_conditions:
        module_cond.dump(output_dir)

    print(f"Stockage temporaire terminé : {len(module_conditions)} fichiers JSON créés dans {output_dir}.")

    conditions_dict = {mod.module: mod.conditions for mod in module_conditions}

    json_file_path = output_dir / "module_conditions.json"
    with open(json_file_path, "w") as f:
        json.dump({"data": conditions_dict}, f, indent=2, sort_keys=True)

    conditions_list = [{"Module": mod, "Condition": cond} for mod, conds in conditions_dict.items() for cond in conds]
    df = pd.DataFrame(conditions_list)
    csv_file_path = output_dir / "module_conditions.csv"
    df.to_csv(csv_file_path, index=False)

    print(f"Résultats sauvegardés sous {json_file_path} et {csv_file_path}.")

    # Debugging: Affichage des conditions avant séparation
    print("\n=== DEBUG: Conditions brutes ===")
    for module, conditions in conditions_dict.items():
        print(f"Module: {module}, Conditions: {conditions}")

    # Collecter toutes les sous-conditions AND/OR
    and_pairs = defaultdict(Counter)
    or_pairs = defaultdict(Counter)
    condition_usage = Counter()

    for module, conditions in conditions_dict.items():
        print(f"\n=== DEBUG: Conditions pour le module {module} ===")
        
        and_conds = []
        or_conds = []
        
        for condition in conditions:
            split_cond = split_conditions(condition)
            print(f"  - Condition originale: {condition}")
            print(f"    - AND: {split_cond['and']}")
            print(f"    - OR: {split_cond['or']}")

            # Ajouter les conditions séparées
            condition_usage.update(split_cond['and'] + split_cond['or'])

            block_and_conds = split_cond['and']  # Regrouper seulement les conditions AND d'un même bloc
            
            # Mise à jour des paires uniquement pour ce bloc (AND)
            for i, cond1 in enumerate(block_and_conds):
                for j, cond2 in enumerate(block_and_conds):
                    if i != j and cond1 != cond2:
                        and_pairs[cond1][cond2] += 1

            and_conds.extend(block_and_conds)  # Ajouter les conditions du bloc à la liste générale
            or_conds.extend(split_cond['or'])  # Ajouter les conditions OR à la liste OR générale

        # Mise à jour des paires OR
        for i, cond1 in enumerate(or_conds):
            for j, cond2 in enumerate(or_conds):
                if i != j and cond1 != cond2:
                    or_pairs[cond1][cond2] += 1


    # Tracer le diagramme des conditions les plus utilisées
    top_conditions = condition_usage.most_common(limit_number)
    if top_conditions:
        conditions, counts = zip(*top_conditions)
        plt.figure(figsize=(12, 6))
        sns.barplot(x=list(conditions), y=list(counts), palette="viridis")
        plt.xticks(rotation=90)
        plt.xlabel("Conditions")
        plt.ylabel("Nombre of uses")
        plt.title(f"Top {limit_number} of conditions most used")
        condition_usage_image_path = output_dir / "top_conditions_usage.png"
        plt.savefig(condition_usage_image_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Diagramm of most used conditions saved in {condition_usage_image_path}")

    # Tracer le diagramme des modules les plus conditionnés
    module_usage = {module: len(conds) for module, conds in conditions_dict.items()}
    top_modules = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)[:limit_number]

    if top_modules:
        modules, module_counts = zip(*top_modules)
        plt.figure(figsize=(12, 6))
        sns.barplot(x=list(modules), y=list(module_counts), palette="mako")
        plt.xticks(rotation=90)
        plt.xlabel("Modules")
        plt.ylabel("Number of Conditions")
        plt.title(f"Top {limit_number} des modules with most conditions")
        module_usage_image_path = output_dir / "top_modules_conditioned.png"
        plt.savefig(module_usage_image_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Diagramm of modules must conditioned saved in {module_usage_image_path}")

  # Supprimer les fichiers JSON 
    for file in output_dir.glob("*.json"):
       file.unlink()
    print("all json files are deleted.")

