from pathlib import Path
import json
import attr
from typing import List

@attr.s(auto_attribs=True)
class Module:
    def __init__(self, name: str, uses: int):
        self.name = name
        self.uses = uses

    def to_dict(self):
        return {
            "name": self.name,
            "uses": self.uses
        }

    def dump(self, output_dir: Path):
        """Sauvegarde les détails du module dans un fichier JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{self.name}_module.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def __repr__(self):
        return f"Module(name={self.name}, uses={self.uses})"

@attr.s(auto_attribs=True)
class MostUsedRoles:
    def __init__(self, name: str, modules: list):
        self.name = name
        self.modules = modules  # Liste d'objets Module

    def to_dict(self):
        return {
            "name": self.name,
            "modules": [module.to_dict() for module in self.modules]
        }

    def dump(self, output_dir: Path):
        """Sauvegarde les détails du rôle et de ses modules dans un fichier JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{self.name}_role.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def __repr__(self):
        return f"MostUsedRoles(name={self.name}, modules={self.modules})"

@attr.s(auto_attribs=True)
class ModuleArguments:
    module: str
    common_args: List[str]

    def dump(self, directory: Path):
        fpath = directory / f"{self.module}_args.json"
        data = {
            "module": self.module,
            "common_args": self.common_args
        }
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath
@attr.s(auto_attribs=True)
class LoopUsage:
    module: str
    loop_percentage: float

    def dump(self, directory: Path):
        fpath = directory / f"{self.module}_loop_usage.json"
        data = {
            "module": self.module,
            "loop_percentage": self.loop_percentage
        }
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath


@attr.s(auto_attribs=True)
class StrongCorrelation:
    module_a: str
    module_b: str
    correlation: float

    def dump(self, directory: Path):
        fpath = directory / f"{self.module_a}_to_{self.module_b}_correlation.json"
        data = {
            "module_a": self.module_a,
            "module_b": self.module_b,
            "correlation": self.correlation
        }
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath

@attr.s(auto_attribs=True)
class ModuleConditions:
    module: str
    conditions: List[str]

    def dump(self, directory: Path):
        fpath = directory / f"{self.module}_conditions.json"
        data = {"module": self.module, "conditions": self.conditions}
        fpath.write_text(json.dumps(data, sort_keys=True, indent=2))
        return fpath


