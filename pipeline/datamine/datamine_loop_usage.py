import os
import yaml
import csv
import pandas as pd
from collections import defaultdict
from typing import Optional
from pipeline.base import Stage, ResultMap
from config import MainConfig
from models.datamine.roles import LoopUsageResult
import util
import json

class DatamineLoopUsage(Stage[LoopUsageResult, MainConfig]):
    dataset_dir_name = 'LoopUsage'  
    roles_dir_name = 'StructuralModels'  

    def report_results(self, results: ResultMap[LoopUsageResult]) -> None:
        """Affiche un résumé des pourcentages d'utilisation de loop."""
        print('--- Datamine Loop Usage ---')
        print(f'Nombre total de modules analysés : {len(results)}')

        for module, loop_usage in results.items():
            print(f'Module: {module}, Utilisation de loop : {loop_usage.data:.2f}%')

    def run(self, _: Optional[ResultMap] = None) -> LoopUsageResult:
        """Exécuter la phase pour analyser l'utilisation de loop par module."""
        roles_directory_path = os.path.join(self.config.output_directory, self.roles_dir_name)
        loop_usage = defaultdict(lambda: [0, 0])  

        if not os.path.exists(roles_directory_path):
            raise FileNotFoundError(f"Le répertoire des rôles '{roles_directory_path}' n'existe pas.")

        def process_yaml_file(file_path):
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)

                for role in data:
                    if isinstance(role, dict) and role.get('role_rev') == "HEAD":
                        for task_file in role.get('role_root', {}).get('task_files', []):
                            for task in task_file.get('content', []):
                                for block in task.get('block', []):
                                    action = block.get('action')
                                    if action:
                                        loop_usage[action][1] += 1
                                        if 'loop' in block:
                                            loop_usage[action][0] += 1

        for filename in os.listdir(roles_directory_path):
            if filename.endswith(".yaml"):
                process_yaml_file(os.path.join(roles_directory_path, filename))

        loop_percentage_per_module = {
            module: (usage[0] / usage[1] * 100 if usage[1] > 0 else 0)
            for module, usage in loop_usage.items()
        }
        
        self.save_results(loop_percentage_per_module)

        print(f"Nombre de fichiers parsés : {len(os.listdir(roles_directory_path))}")

        return LoopUsageResult(data=loop_percentage_per_module)

    def save_results(self, loop_percentage_per_module):
        """Sauvegarde les résultats sous forme de fichier JSON et CSV."""
        dataset_dir_path = os.path.join(self.config.output_directory, self.dataset_dir_name)
        os.makedirs(dataset_dir_path, exist_ok=True)

        json_file_path = os.path.join(dataset_dir_path, "loop_usage_result.json")
        with open(json_file_path, "w") as f:
            json.dump({"data": loop_percentage_per_module}, f, indent=2, sort_keys=True)
        print(f"Les résultats ont été sauvegardés dans '{json_file_path}'.")

        csv_file_path = os.path.join(dataset_dir_path, "loop_usage_percentage_per_module.csv")
        result_df = pd.DataFrame.from_dict(loop_percentage_per_module, orient='index', columns=['Loop Usage Percentage'])
        result_df.index.name = 'Module'
        result_df.to_csv(csv_file_path)
        print(f"Les résultats ont été sauvegardés dans '{csv_file_path}'.")

        self.generate_top_loop_usage_chart(loop_percentage_per_module)

        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
            print(f"Le fichier temporaire '{csv_file_path}' a été supprimé.")

