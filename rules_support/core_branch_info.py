import copy
import json
import re
from .branch_info import BranchInfo
from git import Repo

class CoreBranchInfo(BranchInfo):

    def __init__(self, folder):
        super().__init__(folder)
        self._version = None
        self._init_branch_info()

    @classmethod
    def from_json(cls, json_str):
        attr_dict = json.loads(json_str)
        if not isinstance(attr_dict, dict):
            raise ValueError(f'{cls.__name__}: Error loading incompatible data')
        temp = cls(attr_dict['_folder'])
        return temp

    def to_json(self):
        # the git stuff is not serializable
        temp_dict = copy.deepcopy(self.__dict__)
        temp_dict.pop('_repo')
        return json.dumps(temp_dict)

    def _init_branch_info(self):
        self._version = None
        if self.branch_name == "master" or self.branch_name == "main":
            self._version = "latest"
        else:
            # Core branch handling
            # Feature branch handling
            cap = re.search(r"^feature-|feature\/(.*)$", self.branch_name)
            if not cap is None:
                self._version = cap.group(1)
                print(f"Derived feature branch version: {self.version}")
            else:
                # Release branch handling
                cap = re.search(r"^release-|release\/(.*)$", self.branch_name)
                if not cap is None:
                    self._version = cap.group(1)

    @property
    def version(self):
        return self._version

