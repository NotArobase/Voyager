from collections import Counter, defaultdict
import os
import yaml
import matplotlib.pyplot as plt

def algo(config, roles_dir_name: str, options=None):
    """Analyse l'utilisation de 'when' pour chaque module des modules les plus utilisés."""
    num_modules = options.get("num_modules", 10) if options else 10
    roles_directory_path = os.path.join(config.output_directory, roles_dir_name)  
    modules_per_role = defaultdict(lambda: Counter())
    module_when_counts = Counter()
    module_total_counts = Counter()
    
    if not os.path.exists(roles_directory_path):
        raise FileNotFoundError(f"Roles directory '{roles_directory_path}' does not exist.")

    def process_yaml_file(file_path):
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
                                    modules_per_role[role.get('role_id')][action] += 1
                                    module_total_counts[action] += 1
                                    if 'when' in block:
                                        module_when_counts[action] += 1
    
    for filename in os.listdir(roles_directory_path):
        if filename.endswith(".yaml"):
            process_yaml_file(os.path.join(roles_directory_path, filename))

    # Trier les modules les plus utilisés
    most_used_modules = [module for module, _ in module_total_counts.most_common(num_modules)]
    
    # Calculer le pourcentage d'utilisation de "when"
    module_when_percentages = {module: (module_when_counts[module] / module_total_counts[module]) * 100 
                               for module in most_used_modules if module_total_counts[module] > 0}
    
    return module_when_percentages

def store_results(results, config, filename):
    """Stocke et visualise les résultats de l'analyse."""
    num_modules = config.options.get("num_modules", 10)

    output_file_path = os.path.join(config.output_directory, filename)
    os.makedirs(output_file_path, exist_ok=True)
    
    # Tracer le graphique
    plt.figure(figsize=(12, 6))
    plt.bar(results.keys(), results.values())
    plt.xlabel("Modules")
    plt.ylabel("% d'utilisation de 'when'")
    plt.title(f"Pourcentage d'existence de 'when' pour les {num_modules} modules les plus utilisés")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    output_image_path = os.path.join(output_file_path, "when_usage_percentage.png")
    plt.savefig(output_image_path)
    plt.show()
    
    print(f"Graphique enregistré dans : {output_image_path}")
