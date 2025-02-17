import importlib.util
from typing import Any, Optional
from pipeline.base import Stage, ResultMap
from config import MainConfig

class DatamineStage(Stage[Any, MainConfig]):
    """
    Stage générique qui délègue l'algorithme à un script externe.
    
    Optionnellement (ou pas), le script peut définir une fonction `store_results` pour gérer le stockage.
    """

    def run(self, algo_script_path: str, needs_data: bool, data: Optional[Any] = None) -> ResultMap[Any]:
        """

        :param algo_script_path: Chemin vers le script Python de l'algorithme.
        :param needs_data: Booléen indiquant si l'algorithme nécessite des données.
        :param data: Les données à transmettre à l'algorithme (si besoin).
        :return: Un ResultMap contenant le résultat de l'algorithme.
        """
    
        spec = importlib.util.spec_from_file_location("external_algo", algo_script_path)
        external_algo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(external_algo)

        if not hasattr(external_algo, "run_algo"):
            raise AttributeError("Le script de l'algorithme doit contenir une fonction 'run_algo'.")

        # Exécuter l'algorithme en fonction du paramètre needs_data 
        if needs_data:
            if data is None:
                raise ValueError("L'algorithme nécessite des données, mais aucune donnée n'a été fournie.")
            result = external_algo.run_algo(data, self.config.output_directory)
        else:
            result = external_algo.run_algo(self.config.output_directory)

        # L'idée est de checker si mon script externe contient une fonction store_result. 
        # De sorte, nous n'aurons pas toujours besoin de lancer certains algorithmes (gain de temps et d'energie)    
        if hasattr(external_algo, "store_results"):
            external_algo.store_results(result, self.config.output_directory)

        return ResultMap(result)

    def report_results(self, results: ResultMap[Any]) -> None:
        print("Résultats de l'algorithme :")
        print(results)
