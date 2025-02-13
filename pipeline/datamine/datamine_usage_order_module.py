import os
import yaml
import csv
import pandas as pd
from collections import defaultdict, Counter
from typing import Optional
from pipeline.base import Stage, ResultMap
from config import MainConfig
from models.datamine.roles import ModuleUsageResult, ModuleTransitionResult
import util
import json

class DatamineModuleUsage(Stage[ModuleUsageResult, MainConfig]):
    dataset_dir_name = 'ModuleUsage'  
    roles_dir_name = 'StructuralModels'  

    def report_results(self, results: ResultMap[ModuleUsageResult]) -> None:
        print('--- Datamine Module Usage ---')
        print(f'Nombre total de rôles analysés : {len(results)}')

        for role, usage in results.items():
            print(f'Rôle: {role}, Nombre de modules utilisés: {len(usage.data)}')

    def run(self, _: Optional[ResultMap] = None) -> ModuleUsageResult:
        roles_directory_path = os.path.join(self.config.output_directory, self.roles_dir_name)
        modules_per_role = defaultdict(list)
        module_transitions = defaultdict(Counter)

        if not os.path.exists(roles_directory_path):
            raise FileNotFoundError(f"Le répertoire des rôles '{roles_directory_path}' n'existe pas.")

        def process_yaml_file(file_path):
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)

                for role in data:
                    if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                        role_id = role.get('role_id')
                        task_files = role.get('role_root', {}).get('task_files', [])

                        for task_file in task_files:
                            tasks = task_file.get('content', [])
                            module_sequence = []

                            for task in tasks:
                                for block in task.get('block', []):
                                    action = block.get('action')
                                    if action:
                                        modules_per_role[role_id].append(action)
                                        module_sequence.append(action)

                            for i in range(len(module_sequence) - 1):
                                module_transitions[module_sequence[i]][module_sequence[i + 1]] += 1

        for filename in os.listdir(roles_directory_path):
            if filename.endswith(".yaml"):
                process_yaml_file(os.path.join(roles_directory_path, filename))

        module_usage_matrix = {role: Counter(modules) for role, modules in modules_per_role.items()}
        transition_matrix = {module: dict(transitions) for module, transitions in module_transitions.items()}
        
        transition_probabilities = {
            module: {target: count / sum(transitions.values()) for target, count in transitions.items()}
            for module, transitions in transition_matrix.items()
        }

        self.save_results(module_usage_matrix, transition_probabilities)

        print(f"Nombre de fichiers parsés : {len(os.listdir(roles_directory_path))}")

        return ModuleUsageResult(data=module_usage_matrix)

    def save_results(self, module_usage_matrix, transition_probabilities):
        dataset_dir_path = os.path.join(self.config.output_directory, self.dataset_dir_name)
        os.makedirs(dataset_dir_path, exist_ok=True)

        json_file_path = os.path.join(dataset_dir_path, "module_usage_result.json")
        with open(json_file_path, "w") as f:
            json.dump({"data": module_usage_matrix}, f, indent=2, sort_keys=True)
        print(f"Les résultats ont été sauvegardés dans '{json_file_path}'.")

        json_transitions_file = os.path.join(dataset_dir_path, "module_transition_result.json")
        with open(json_transitions_file, "w") as f:
            json.dump({"data": transition_probabilities}, f, indent=2, sort_keys=True)
        print(f"Les résultats de transition ont été sauvegardés dans '{json_transitions_file}'.")

        pd.DataFrame.from_dict(module_usage_matrix, orient='index').to_csv(os.path.join(dataset_dir_path, "module_usage_matrix.csv"))
        pd.DataFrame.from_dict(transition_probabilities, orient='index').to_csv(os.path.join(dataset_dir_path, "module_transition_probabilities.csv"))

        print("Sauvegarde des matrices terminée.")
