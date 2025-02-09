import os
import yaml
import csv
from collections import defaultdict, Counter
import pandas as pd
from typing import Optional
from pipeline.base import Stage, ResultMap
from config import MainConfig
from models.datamine.roles import CommonArgsResult
import util
import json

class DatamineCommonArgs(Stage[CommonArgsResult, MainConfig]):
    dataset_dir_name = 'DatamineCommunRoles'  
    roles_dir_name = 'StructuralModels'  
    def report_results(self, results: ResultMap[CommonArgsResult]) -> None:
        """Affiche un résumé des arguments communs extraits."""
        print('--- Datamine Common Args ---')
        print(f'Nombre total de modules analysés : {len(results)}')

        for module, common_args in results.items():
            print(f'Module: {module}, Arguments communs: {common_args.data}')

    def run(self, _: Optional[ResultMap] = None) -> CommonArgsResult:
        """Exécuter la phase pour identifier les arguments communs des modules."""
        roles_directory_path = os.path.join(self.config.output_directory, self.roles_dir_name)
        modules_args = defaultdict(list)

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
                                    args = block.get('args', {})
                                    if action and isinstance(args, dict):
                                        modules_args[action].extend(args.keys())

        for filename in os.listdir(roles_directory_path):
            if filename.endswith(".yaml"):
                process_yaml_file(os.path.join(roles_directory_path, filename))

        common_args_per_module = {module: list(set(args)) for module, args in modules_args.items()}
        
        self.save_results(common_args_per_module)

        print(f"Nombre de fichiers parsés : {len(os.listdir(roles_directory_path))}")

        return CommonArgsResult(data=common_args_per_module)

    def save_results(self, common_args_per_module):
        """Sauvegarde les résultats sous forme de fichier JSON et CSV."""
        dataset_dir_path = os.path.join(self.config.output_directory, self.dataset_dir_name)
        os.makedirs(dataset_dir_path, exist_ok=True)

        json_file_path = os.path.join(dataset_dir_path, "common_args_result.json")
        with open(json_file_path, "w") as f:
            json.dump({"data": common_args_per_module}, f, indent=2, sort_keys=True)
        print(f"Les résultats ont été sauvegardés dans '{json_file_path}'.")

        csv_file_path = os.path.join(dataset_dir_path, "common_args_per_module.csv")
        result_df = pd.DataFrame.from_dict(common_args_per_module, orient='index')
        result_df.index.name = 'Module'
        result_df.to_csv(csv_file_path)
        print(f"Les résultats ont été sauvegardés dans '{csv_file_path}'.")


       


    def generate_top_arguments_chart(self, common_args_per_module):
        """Génère un graphique des 50 arguments les plus utilisés."""
        dataset_dir_path = os.path.join(self.config.output_directory, self.dataset_dir_name)

        arg_usage = Counter(arg for args in common_args_per_module.values() for arg in args)
        top_50_args = arg_usage.most_common(50)

        if top_50_args:
            args, counts = zip(*top_50_args)
            util.create_bar_chart(
                x_data=args,
                y_data=counts,
                title="Top 50 Most Used Arguments",
                xlabel="Arguments",
                ylabel="Usage Count",
                output_directory=self.config.output_directory,
                output_dataset_name=self.dataset_dir_name,
                output_filename="top_50_arguments.png",
                figsize=(12, 8),
            )
            print("Graphique des 50 arguments les plus utilisés généré avec succès.")
