import json
from pathlib import Path
import attr
from models.base import Model
from typing import Sequence
from typing import Dict, List
import json
import pandas as pd

@attr.s(auto_attribs=True)
class Module(Model):
    name: str
    uses: int

    @property
    def id(self) -> str:
        return self.name

@attr.s(auto_attribs=True)
class MostUsedRoles(Model):
    name: str
    modules: Sequence[Module]

    @property
    def id(self) -> str:
        return self.name

    def dump(self, directory: Path) -> Path:
        fpath = directory / f'{self.name}.json'
        # Create a dictionary to represent the object
        data = {
            "name": self.name,
            "modules": [attr.asdict(module) for module in self.modules]
        }
        # Write the data to the file
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath


@attr.s(auto_attribs=True)
class ModuleCorrelation(Model):
    module_a: str
    module_b: str
    correlation: float  # Coefficient de corrélation (entre -1 et 1)

    @property
    def id(self) -> str:
        return f"{self.module_a}_{self.module_b}"

    def dump(self, directory: Path) -> Path:
        """Stocke la corrélation dans un fichier JSON."""
        fpath = directory / f'{self.module_a}_{self.module_b}.json'
        data = {
            "module_a": self.module_a,
            "module_b": self.module_b,
            "correlation": self.correlation
        }
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath


@attr.s(auto_attribs=True)
class CommonArgsResult(Model):
    """Classe pour stocker les arguments communs des modules."""
    data: Dict[str, List[str]]  

    @property
    def id(self) -> str:
        """Identifiant unique."""
        return "common_args_result"

    def dump(self, directory: Path) -> Path:
        """Sauvegarde les résultats en JSON dans un fichier."""
        file_path = directory / "common_args_result.json"
        with open(file_path, "w") as f:
            json.dump(self.to_json_obj(), f, indent=2, sort_keys=True)
        return file_path

    @classmethod
    def load(cls, id: str, file_path: Path) -> "CommonArgsResult":
        """Charge les résultats à partir d'un fichier JSON."""
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if "data" not in data:
                    raise KeyError(f"Le fichier JSON {file_path} ne contient pas la clé 'data'.")
                return cls(data=data["data"])
            except json.JSONDecodeError:
                raise ValueError(f"Erreur lors de la lecture du fichier JSON {file_path}.")
    


@attr.s(auto_attribs=True)
class LoopUsageResult(Model):
    """Classe pour stocker les pourcentages d'utilisation de loop par module."""
    data: Dict[str, float]  

    @property
    def id(self) -> str:
        return "loop_usage_result"

    def dump(self, directory: Path) -> Path:
        """Sauvegarde les résultats sous forme de JSON."""
        file_path = directory / "loop_usage_result.json"
        with open(file_path, "w") as f:
            json.dump({"data": self.data}, f, indent=2, sort_keys=True)
        return file_path

    @classmethod
    def load(cls, id: str, file_path: Path) -> "LoopUsageResult":
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if "data" not in data:
                    raise KeyError(f"Le fichier JSON {file_path} ne contient pas la clé 'data'.")
                return cls(data=data["data"])
            except json.JSONDecodeError:
                raise ValueError(f"Erreur lors de la lecture du fichier JSON {file_path}.")



@attr.s(auto_attribs=True)
class ModuleUsageResult(Model):
    """Classe pour stocker l'utilisation des modules par rôle."""
    data: Dict[str, Dict[str, int]]

    @property
    def id(self) -> str:
        return "module_usage_result"

    def dump(self, directory: Path) -> Path:
        file_path = directory / "module_usage_result.json"
        with open(file_path, "w") as f:
            json.dump({"data": self.data}, f, indent=2, sort_keys=True)
        return file_path

    @classmethod
    def load(cls, id: str, file_path: Path) -> "ModuleUsageResult":
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if "data" not in data:
                    raise KeyError(f"Le fichier JSON {file_path} ne contient pas la clé 'data'.")
                return cls(data=data["data"])
            except json.JSONDecodeError:
                raise ValueError(f"Erreur lors de la lecture du fichier JSON {file_path}.")

@attr.s(auto_attribs=True)
class ModuleTransitionResult(Model):
    data: Dict[str, Dict[str, float]]  

    @property
    def id(self) -> str:
        return "module_transition_result"

    def dump(self, directory: Path) -> Path:
        file_path = directory / "module_transition_result.json"
        with open(file_path, "w") as f:
            json.dump({"data": self.data}, f, indent=2, sort_keys=True)
        return file_path

    @classmethod
    def load(cls, id: str, file_path: Path) -> "ModuleTransitionResult":
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if "data" not in data:
                    raise KeyError(f"Le fichier JSON {file_path} ne contient pas la clé 'data'.")
                return cls(data=data["data"])
            except json.JSONDecodeError:
                raise ValueError(f"Erreur lors de la lecture du fichier JSON {file_path}.")
