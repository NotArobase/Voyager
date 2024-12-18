from collections import defaultdict
from models.structural.role import MultiStructuralRoleModel
from pipeline.extract.extract_structural_models import ExtractStructuralModels
from pipeline.base import ResultMap, Stage

from config import MainConfig

from models.datamine.roles import MostUsedRoles

class DatamineRoles(Stage[MostUsedRoles, MainConfig], requires=ExtractStructuralModels):

    dataset_dir_name = 'DatamineRoles'

    def run(self, extract_structural_models: ResultMap[MultiStructuralRoleModel]) -> ResultMap[MostUsedRoles]:
        """Run the stage."""
        mostUsedRoles = self.algo(extract_structural_models)
    
        return ResultMap(mostUsedRoles)

    def report_results(self, results: ResultMap[MostUsedRoles]) -> None:
        """Report statistics on gathered roles."""
        print('--- Role Datamine ---')
        print(f'Extracted {len(results)} roles')

    def algo(self, models):
        """ Go over each roles and read the yaml that we got from the previous stage"""
        # Use a defaultdict to store modules per role
        modules_per_role = defaultdict(list)


        for role in models.values():
            # print(role)
            role_id = role.role_id
            print(f"Traitement du rôle avec ID : {role_id}")
            
            for model in role.structural_models:
                role_rev = model.role_rev
                task_files = model.role_root.task_files

                if role_rev == "HEAD":
                    for task_file in task_files:
                        for task in task_file:

                            for block in task.block:
                                print(dir(block))
                                action = block.action
                                if action:
                                    modules_per_role[role_id].append(action)

        return dict(modules_per_role)   