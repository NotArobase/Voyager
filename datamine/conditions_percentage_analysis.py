from collections import Counter, defaultdict
import os
import yaml
import matplotlib.pyplot as plt

def algo(config, roles_dir_name: str, options=None):
    """Analyse l'utilisation de 'when' pour chaque module et affiche les modules les plus utilisés."""
    
    num_modules = options.get("num_modules", 25) if options else 25
    roles_directory_path = os.path.join(config.output_directory, roles_dir_name)  
    module_when_counts = Counter()  # Nombre de fois où 'when' est utilisé par module
    module_total_counts = Counter()  # Nombre total d'apparitions du module

    if not os.path.exists(roles_directory_path):
        raise FileNotFoundError(f"Roles directory '{roles_directory_path}' does not exist.")

    def process_yaml_file(file_path):
        """Parcourt un fichier YAML et met à jour les statistiques des modules."""
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            for role in data:
                if isinstance(role, dict):
                    task_files = role.get('role_root', {}).get('task_files', [])
                    for task_file in task_files:
                        tasks = task_file.get('content', [])
                        for task in tasks:
                            for block in task.get('block', []):
                                action = block.get('action')
                                if action:
                                    module_total_counts[action] += 1  # Compte chaque apparition du module
                                    if 'when' in block:
                                        module_when_counts[action] += 1  # Compte les cas où 'when' est utilisé

    # Parcourir tous les fichiers YAML dans le répertoire
    for filename in os.listdir(roles_directory_path):
        if filename.endswith(".yaml"):
            process_yaml_file(os.path.join(roles_directory_path, filename))

    # Calculer le pourcentage d'utilisation de "when" pour chaque module
    module_when_percentages = {
        module: (module_when_counts[module] / module_total_counts[module]) * 100
        for module in module_total_counts if module_total_counts[module] > 0
    }

    # Trier les modules par pourcentage décroissant et garder les top `num_modules`
    sorted_modules = sorted(module_when_percentages.items(), key=lambda x: x[1], reverse=True)[:num_modules]

    return dict(sorted_modules)


def store_results(results, config, filename):
    
    output_file_path = os.path.join(config.output_directory, filename)
    os.makedirs(output_file_path, exist_ok=True)

    # the graph 
    plt.figure(figsize=(12, 6))
    modules, percentages = zip(*results.items())
    
    plt.bar(modules, percentages, color='blue')
    plt.xlabel("Modules")
    plt.ylabel("Pourcentage of 'when'" )
    plt.title(f"Top {len(results)} modules with the highest percentage use of 'when'")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    output_image_path = os.path.join(output_file_path, "when_usage_percentage.png")
    plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Graph saved in: {output_image_path}")
