import os
import csv
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from pipeline.base import ResultMap, Stage
from config import MainConfig
from models.datamine.roles import MostUsedRoles
from pipeline.datamine.datamine_roles import DatamineRoles

class AnalyzeModuleUsage(Stage[None, MainConfig], requires=DatamineRoles):

    dataset_dir_name = 'DatamineRoles'

    def run(self, most_used_roles: ResultMap[MostUsedRoles]) -> None:
        """Run the analysis on module usage."""
        # Gather all modules and roles from the input
        modules_per_role = defaultdict(list)
        for role in most_used_roles:
            modules_per_role[role.name] = [module.name for module in role.modules]

        # Create a set of all unique modules
        all_modules = list(set(module for modules in modules_per_role.values() for module in modules))

        # Initialize the module usage matrix
        module_usage_matrix = {role_id: {module: 0 for module in all_modules} for role_id in modules_per_role}

        # Populate the matrix with counts
        for role_id, modules in modules_per_role.items():
            for module in modules:
                if module in all_modules:
                    module_usage_matrix[role_id][module] += 1

        # Write the matrix to a CSV file
        output_file = os.path.join(self.config.output_directory, "modules_par_role.csv")
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Role"] + all_modules)
            for role_id, module_counts in module_usage_matrix.items():
                writer.writerow([role_id] + [module_counts[module] for module in all_modules])
        print(f"Module usage matrix saved to {output_file}.")

        # Calculate module usage and generate top 50 modules plot
        module_usage = {module: 0 for module in all_modules}
        for role_id, module_counts in module_usage_matrix.items():
            for module, count in module_counts.items():
                module_usage[module] += count

        sorted_usage = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)
        top_50_modules = sorted_usage[:50]

        # Plot the top 50 modules
        modules, counts = zip(*top_50_modules)
        plt.figure(figsize=(12, 8))
        plt.bar(modules, counts)
        plt.xticks(rotation=90)
        plt.xlabel("Modules")
        plt.ylabel("Usage Count")
        plt.title("Top 50 Most Used Modules")
        plt.tight_layout()

        # Save and display the plot
        plot_file = os.path.join(self.config.output_directory, "top_50_modules.png")
        plt.savefig(plot_file)
